from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from backend.db.postgres import engine, Base
from backend.core.processor import process_signals
from backend.api.health import throughput_logger
from backend.api import ingestion, health, incidents

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Start background tasks
    task_processor = asyncio.create_task(process_signals())
    task_logger = asyncio.create_task(throughput_logger())
    
    yield
    
    task_processor.cancel()
    task_logger.cancel()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(ingestion.router, prefix="/api")
app.include_router(incidents.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
