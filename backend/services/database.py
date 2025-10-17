from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

load_dotenv()

# Define logger
logger = logging.getLogger("database")
logging.basicConfig(level=logging.INFO)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./presm.db")

engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """Initialize the database and create tables."""
    async with engine.begin() as conn:
        # Import models to register them with Base
        from models.product import Base as ProductBase
        from models.cart import Base as CartBase
        
        # Create all tables using a shared metadata if possible, but since separate Bases, create separately
        await conn.run_sync(ProductBase.metadata.create_all)
        await conn.run_sync(CartBase.metadata.create_all)
        logger.info("✅ Created tables: products, carts")