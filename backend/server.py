from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import logging
import uuid
import os

# Import database utilities
from services.database import connect_to_mongo, close_mongo_connection, database

# Import routes
from routes.products import router as products_router
from routes.gang_sheets import router as gang_sheets_router
from routes.cart import router as cart_router
from routes.shopify import router as shopify_router
from routes.auth import router as auth_router

# ---------------------------------------------------------------------
# Environment Setup
# ---------------------------------------------------------------------
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# ---------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------
app = FastAPI(
    title="PRESM Technologies API",
    description="Backend API for PRESM Technologies DTF transfer platform",
    version="1.0.0"
)

api_router = APIRouter(prefix="/api")

# ---------------------------------------------------------------------
# Models for simple status checks
# ---------------------------------------------------------------------
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StatusCheckCreate(BaseModel):
    client_name: str


# ---------------------------------------------------------------------
# Health and Root Endpoints
# ---------------------------------------------------------------------
@api_router.get("/")
async def root():
    return {"message": "PRESM Technologies API", "status": "running"}


@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# ---------------------------------------------------------------------
# Include all Routers
# ---------------------------------------------------------------------
api_router.include_router(products_router)
api_router.include_router(gang_sheets_router)
api_router.include_router(cart_router)
api_router.include_router(shopify_router)
api_router.include_router(auth_router)

app.include_router(api_router)

# ---------------------------------------------------------------------
# ✅ CORS Configuration
# ---------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://presmtechnologies.com",
        "https://www.presmtechnologies.com",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------
# React Frontend Serving (Production)
# ---------------------------------------------------------------------
FRONTEND_BUILD_PATH = Path(__file__).parent.parent / "frontend" / "build"
if FRONTEND_BUILD_PATH.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_BUILD_PATH / "static")), name="static")

    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        """Serve React app for all non-API routes"""
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")

        file_path = FRONTEND_BUILD_PATH / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        return FileResponse(FRONTEND_BUILD_PATH / "index.html")


# ---------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("server")

# ---------------------------------------------------------------------
# Startup and Shutdown Events
# ---------------------------------------------------------------------
@app.on_event("startup")
async def startup_db_client():
    try:
        await connect_to_mongo()

        # ✅ Proper database connection check
        if database.database is not None:
            from services.product_service import ProductService
            from services.gang_sheet_service import GangSheetService
            from services.cart_service import CartService

            import services.product_service
            import services.gang_sheet_service
            import services.cart_service

            services.product_service.product_service = ProductService()
            services.gang_sheet_service.gang_sheet_service = GangSheetService()
            services.cart_service.cart_service = CartService()

            logger.info("✅ Services initialized successfully")
            await initialize_mock_data()
        else:
            logger.warning("⚠️ Database not connected — skipping service initialization")

    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        logger.info("Server will continue without database support")


@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()
    logger.info("🧹 MongoDB connection closed")


# ---------------------------------------------------------------------
# Initialize Mock Data
# ---------------------------------------------------------------------
async def initialize_mock_data():
    """Initialize database with mock products if empty"""
    if database.database is None:
        logger.info("Skipping mock data initialization - database not available")
        return

    from utils import get_product_service
    try:
        product_service = get_product_service()
        products = await product_service.get_products(limit=1)
        if products:
            return  # Already initialized

        logger.info("Initializing mock product data...")

        mock_products = [
            {
                "name": "Standard DTF Transfer",
                "category": "dtf-transfers",
                "price": 2.50,
                "image": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=400&h=400&fit=crop",
                "description": "High-quality direct-to-film transfers with vibrant colors and excellent durability.",
                "features": ["Premium PET film", "Vivid colors", "Cold peel", "Machine washable"],
                "sizes": ["2x2", "3x3", "4x4", "5x5", "6x6", "8x8", "10x10", "12x12"],
                "min_quantity": 1,
                "max_quantity": 1000,
                "inventory": 100,
                "status": "active"
            },
            {
                "name": "Gang Sheet 12x16",
                "category": "gang-sheets",
                "price": 18.99,
                "image": "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=400&fit=crop",
                "description": "Maximize efficiency with our 12x16 gang sheets. Perfect for multiple small designs.",
                "features": ["12x16 inch sheet", "Multiple designs", "Cost effective", "Fast turnaround"],
                "sizes": ["12x16"],
                "min_quantity": 1,
                "max_quantity": 100,
                "inventory": 50,
                "status": "active"
            },
            {
                "name": "Professional Heat Press 15x15",
                "category": "heat-presses",
                "price": 299.99,
                "image": "https://images.unsplash.com/photo-1586796676553-f4c9c5ba5b12?w=400&h=400&fit=crop",
                "description": "Professional-grade heat press machine with digital temperature and time control.",
                "features": ["15x15 inch platen", "Digital controls", "Even heat distribution", "1-year warranty"],
                "sizes": ["15x15"],
                "min_quantity": 1,
                "max_quantity": 10,
                "inventory": 25,
                "status": "active"
            },
        ]

        from models.product import ProductCreate
        for data in mock_products:
            product = ProductCreate(**data)
            await product_service.create_product(product)

        logger.info("✅ Mock product data initialized successfully")

    except Exception as e:
        logger.warning(f"⚠️ Could not initialize mock data: {e}")
