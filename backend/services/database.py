from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

database = Database()

async def get_database():
    return database.database

async def connect_to_mongo():
    """Create database connection"""
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.getenv('DB_NAME', 'presm_dtf')
    
    try:
        database.client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
        temp_db = database.client[db_name]
        await database.client.admin.command('ping')
        database.database = temp_db
        print(f"Connected to MongoDB at {mongo_url}")

        # ✅ ADD THIS LINE HERE
        print(f"✅ Connected to DB: {db_name}")

    except Exception as e:
        print(f"Warning: Could not connect to MongoDB: {e}")
        print("Running in limited mode without database")
        database.database = None
        database.client = None


async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()
        print("Disconnected from MongoDB")

# Collection getters
def get_products_collection():
    if database.database is None:
        raise RuntimeError("Database not initialized")
    return database.database.products

def get_gang_sheets_collection():
    if database.database is None:
        raise RuntimeError("Database not initialized")
    return database.database.gang_sheets

def get_orders_collection():
    if database.database is None:
        raise RuntimeError("Database not initialized")
    return database.database.orders

def get_carts_collection():
    if database.database is None:
        raise RuntimeError("Database not initialized")
    return database.database.carts

def get_users_collection():
    if database.database is None:
        raise RuntimeError("Database not initialized")
    return database.database.users