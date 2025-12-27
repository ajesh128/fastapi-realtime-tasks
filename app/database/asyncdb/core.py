from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorGridFSBucket

from app.core.config import Config

MONGO_URI = Config.MONGO_URI
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()