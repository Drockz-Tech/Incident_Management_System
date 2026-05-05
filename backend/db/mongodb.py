from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings

client = AsyncIOMotorClient(settings.MONGODB_URL)
mongo_db = client.ims_db

def get_mongo_db():
    return mongo_db
