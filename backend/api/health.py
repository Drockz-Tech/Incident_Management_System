from fastapi import APIRouter
from backend.api.ingestion import metrics
import asyncio

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok", "signals_received": metrics.signals_received}

async def throughput_logger():
    """Prints throughput every 5 seconds."""
    last_count = 0
    while True:
        await asyncio.sleep(5)
        current_count = metrics.signals_received
        throughput = (current_count - last_count) / 5
        print(f"Throughput: {throughput} Signals/sec")
        last_count = current_count
