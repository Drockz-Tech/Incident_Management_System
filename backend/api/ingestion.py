from fastapi import APIRouter, HTTPException
from backend.models.schemas import SignalPayload
from backend.core.ratelimit import check_rate_limit
from backend.core.processor import signal_queue
import asyncio

router = APIRouter()

class Metrics:
    signals_received: int = 0

metrics = Metrics()

@router.post("/signals")
async def ingest_signal(payload: SignalPayload):
    is_allowed = await check_rate_limit("global")
    if not is_allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    try:
        signal_queue.put_nowait(payload)
    except asyncio.QueueFull:
        raise HTTPException(status_code=503, detail="Server busy")
        
    metrics.signals_received += 1
    return {"status": "accepted"}
