from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger("database")
logging.basicConfig(level=logging.INFO)

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

database = Database()

async def get_database():
    if database.database is None:
        logger.warning("Database not initialized, returning None")
        return None
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
        logger.info(f"Connected to MongoDB at {mongo_url}, DB: {db_name}")
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        database.database = None
        database.client = None

async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()
        logger.info("Disconnected from MongoDB")

def get_products_collection():
    if database.database is None:
        logger.error("Database not initialized")
        raise RuntimeError("Database not initialized")
    return database.database.products

def get_carts_collection():
    if database.database is None:
        logger.error("Database not initialized")
        raise RuntimeError("Database not initialized")
    return database.database.carts