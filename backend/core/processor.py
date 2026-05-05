import asyncio
from typing import List
import uuid
import datetime
from collections import defaultdict
from backend.db.redis_client import get_redis
from backend.db.mongodb import get_mongo_db
from backend.db.postgres import AsyncSessionLocal
from backend.models.schemas import SignalPayload
from backend.models.domain import WorkItem, IncidentState
from backend.core.workflow import determine_alert_level
from sqlalchemy import select

# In-memory queue to handle bursts with maxsize to prevent OOM
signal_queue = asyncio.Queue(maxsize=50000)

async def debounce_signal(component_id: str) -> bool:
    """
    Returns True if signal is debounced.
    """
    redis = await get_redis()
    key = f"debounce:{component_id}"
    is_new = await redis.setnx(key, "1")
    if is_new:
        await redis.expire(key, 10) # 10 seconds debounce window
        return False
    return True

async def get_active_work_item_id(component_id: str, sample_signal: SignalPayload) -> str | None:
    redis = await get_redis()
    cache_key = f"active_work_item:{component_id}"
    
    # 1. Check if we have an active work item cached
    cached_id = await redis.get(cache_key)
    if cached_id:
        return cached_id.decode('utf-8')
        
    # 2. Prevent concurrent DB hits by debouncing
    is_debounced = await debounce_signal(component_id)
    
    # 3. Check Postgres for an existing OPEN/INVESTIGATING WorkItem
    work_item_id = None
    async with AsyncSessionLocal() as session:
        query = select(WorkItem).where(
            WorkItem.component_id == component_id,
            WorkItem.state.in_([IncidentState.OPEN, IncidentState.INVESTIGATING])
        )
        result = await session.execute(query)
        existing = result.scalars().first()
        
        if existing:
            work_item_id = existing.id
        elif not is_debounced:
            # 4. Create new WorkItem if debouncing allows it
            alert_level = determine_alert_level(sample_signal)
            new_item = WorkItem(
                id=str(uuid.uuid4()),
                component_id=component_id,
                state=IncidentState.OPEN,
                alert_level=alert_level
            )
            session.add(new_item)
            await session.commit()
            work_item_id = new_item.id
            
    # Cache the ID for the remainder of the 10-second debounce window to link future burst signals
    if work_item_id:
        await redis.setex(cache_key, 10, work_item_id)
        
    return work_item_id

async def process_signals():
    """Background worker continuously reading from the queue."""
    while True:
        try:
            batch = []
            try:
                for _ in range(100):
                    signal = signal_queue.get_nowait()
                    batch.append(signal)
            except asyncio.QueueEmpty:
                if not batch:
                    signal = await signal_queue.get()
                    batch.append(signal)
            
            if batch:
                await handle_batch(batch)
                
        except Exception as e:
            print(f"Error in processor: {e}")

async def handle_batch(signals: List[SignalPayload]):
    # Group by component_id to minimize DB lookups
    by_component = defaultdict(list)
    for s in signals:
        by_component[s.component_id].append(s)

    mongo_db = get_mongo_db()
    all_docs = []
    
    for component_id, component_signals in by_component.items():
        # Get or create active work item ID
        work_item_id = await get_active_work_item_id(component_id, component_signals[0])
        
        # Prepare MongoDB documents linked to the WorkItem
        for s in component_signals:
            doc = s.model_dump()
            doc["timestamp"] = datetime.datetime.now(datetime.timezone.utc)
            if work_item_id:
                doc["work_item_id"] = work_item_id
            all_docs.append(doc)

    if all_docs:
        await mongo_db.raw_signals.insert_many(all_docs)
