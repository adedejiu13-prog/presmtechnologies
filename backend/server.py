from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.database import init_db
from routes.shopify import router as shopify_router
from routes.cart import router as cart_router
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("backend")

app = FastAPI(
    title="PRESM Backend API",
    description="Backend API for PRESM Technologies DTF transfer platform",
    version="1.0.0"
)

FRONTEND_ORIGINS = [
    "https://presmtechnologies.com",
    "http://localhost:3000",
    "https://fictional-meme-979vqvw5xp7v37r45-5000.app.github.dev"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(shopify_router, prefix="/api")
app.include_router(cart_router)

@app.on_event("startup")
async def startup_event():
    try:
        await init_db()
        logger.info("✅ SQLite database initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize SQLite database: {e}")
        raise

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

from sqlalchemy import select
from models.product import Product
from services.database import SessionLocal
@app.get("/debug/products")
async def debug_products():
    async with SessionLocal() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()
        return [{"shopify_id": p.shopify_id, "name": p.name, "price": p.price} for p in products]