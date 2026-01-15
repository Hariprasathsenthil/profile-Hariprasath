from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None
    
db = Database()

async def get_database():
    return db.client[settings.DATABASE_NAME]

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    print(f"Connected to MongoDB at {settings.MONGODB_URL}")
    
async def close_mongo_connection():
    db.client.close()
    print("Closed MongoDB connection")

async def get_users_collection():
    database = await get_database()
    return database.users

async def get_complaints_collection():
    database = await get_database()
    return database.complaints

async def get_escalation_rules_collection():
    database = await get_database()
    return database.escalation_rules

async def get_notifications_collection():
    database = await get_database()
    return database.notifications

async def get_escalation_history_collection():
    database = await get_database()
    return database.escalation_history
