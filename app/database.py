from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.config import settings


class Database:
    client: Optional[AsyncIOMotorClient] = None


db = Database()


async def connect_to_mongo():
    """Create database connection"""
    db.client = AsyncIOMotorClient(
        settings.mongodb_url,
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=20000,
    )
    
    try:
        await db.client.admin.command("ping")
    except Exception as e:
        raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")
    
    database = db.client[settings.database_name]
    
    await create_indexes(database)
    
    return database


async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()


async def create_indexes(database):
    """Create database indexes for better performance"""
    ratings_collection = database.ratings
    await ratings_collection.create_index("user_id")
    await ratings_collection.create_index("item_id")
    await ratings_collection.create_index([("user_id", 1), ("item_id", 1)], unique=True)
    
    items_collection = database.items
    await items_collection.create_index("item_type")
    await items_collection.create_index([("item_type", 1), ("genres", 1)])
    
    users_collection = database.users
    await users_collection.create_index("email", unique=True)
    await users_collection.create_index("username")


async def get_database():
    """Get database instance"""
    if db.client is None:
        await connect_to_mongo()
    return db.client[settings.database_name]
