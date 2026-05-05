from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from backend.db.postgres import get_db
from backend.models.domain import WorkItem
from backend.models.schemas import WorkItemResponse, StateTransitionRequest
from backend.core.workflow import transition_state

router = APIRouter()

@router.get("/incidents", response_model=List[WorkItemResponse])
async def get_incidents(session: AsyncSession = Depends(get_db)):
    query = select(WorkItem).order_by(WorkItem.created_at.desc())
    result = await session.execute(query)
    items = result.scalars().all()
    return items

@router.post("/incidents/{incident_id}/transition", response_model=WorkItemResponse)
async def transition_incident(
    incident_id: str, 
    request: StateTransitionRequest, 
    session: AsyncSession = Depends(get_db)
):
    from sqlalchemy.orm import selectinload
    query = select(WorkItem).options(selectinload(WorkItem.rca)).where(WorkItem.id == incident_id)
    result = await session.execute(query)
    work_item = result.scalars().first()
    
    if not work_item:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    updated_item = await transition_state(session, work_item, request.state, request.rca)
    return updated_item
    
@router.get("/incidents/{incident_id}/signals")
async def get_incident_signals(incident_id: str):
    from backend.db.mongodb import get_mongo_db
    from backend.db.postgres import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        query = select(WorkItem).where(WorkItem.id == incident_id)
        result = await session.execute(query)
        work_item = result.scalars().first()
        if not work_item:
            raise HTTPException(status_code=404, detail="Incident not found")
            
    mongo_db = get_mongo_db()
    cursor = mongo_db.raw_signals.find({"component_id": work_item.component_id}).sort("timestamp", -1).limit(100)
    signals = await cursor.to_list(length=100)
    
    for s in signals:
        s["_id"] = str(s["_id"])
        if "timestamp" in s:
            s["timestamp"] = s["timestamp"].isoformat()
            
    return signals
