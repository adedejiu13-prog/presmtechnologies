from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.database import init_db, SessionLocal
from routes.shopify import router as shopify_router
from routes.cart import router as cart_router
from models.product import Product
from routes.gang_sheets import router as gang_router
from sqlalchemy import select
import logging
from pathlib import Path
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()

# --- Configure logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("backend")

# --- Initialize FastAPI ---
app = FastAPI(
    title="PRESM Backend API",
    description="Backend API for PRESM Technologies DTF transfer platform",
    version="1.0.0"
)

# --- CORS Configuration ---
ALLOWED_ORIGINS = [
    "https://presmtechnologies.com",
    "https://presmtechnologies-git-main-trons-projects-cebadc57.vercel.app",
    "https://www.presmtechnologies.com",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, PUT, DELETE
    allow_headers=["*"],            # Allow custom headers
)

# --- Routers ---
app.include_router(shopify_router, prefix="/api")
app.include_router(cart_router)
app.include_router(gang_router)
# --- Startup event ---
@app.on_event("startup")
async def startup_event():
    try:
        await init_db()
        logger.info("✅ SQLite database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize SQLite database: {e}")
        raise

# --- Health check endpoint ---
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# --- Debug endpoint for products ---
@app.get("/debug/products")
async def debug_products():
    async with SessionLocal() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()
        return [
            {"shopify_id": p.shopify_id, "name": p.name, "price": p.price}
            for p in products
        ]
