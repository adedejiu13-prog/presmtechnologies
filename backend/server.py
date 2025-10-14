from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime

# Import database and services
from services.database import connect_to_mongo, close_mongo_connection, database
# Import services will be done after database connection

# Import routes
from routes.products import router as products_router
from routes.gang_sheets import router as gang_sheets_router
from routes.cart import router as cart_router
from routes.shopify import router as shopify_router
from routes.auth import router as auth_router

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app without a prefix
app = FastAPI(
    title="PRESM Technologies API",
    description="Backend API for PRESM Technologies DTF transfer platform",
    version="1.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models for basic status checks
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StatusCheckCreate(BaseModel):
    client_name: str


# Basic health check routes
@api_router.get("/")
async def root():
    return {"message": "PRESM Technologies API", "status": "running"}


@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# Include all routers
api_router.include_router(products_router)
api_router.include_router(gang_sheets_router)
api_router.include_router(cart_router)
api_router.include_router(shopify_router)
api_router.include_router(auth_router)

# Include the main router in the app
app.include_router(api_router)

# ✅ FIXED: Proper CORS middleware setup
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

# Serve static files from React build (for production)
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


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Startup and shutdown events
@app.on_event("startup")
async def startup_db_client():
    try:
        await connect_to_mongo()

        # Only initialize services if database is available
        if database.database:
            from services.product_service import ProductService
            from services.gang_sheet_service import GangSheetService
            from services.cart_service import CartService

            # Set global service instances
            import services.product_service
            import services.gang_sheet_service
            import services.cart_service

            services.product_service.product_service = ProductService()
            services.gang_sheet_service.gang_sheet_service = GangSheetService()
            services.cart_service.cart_service = CartService()

            await initialize_mock_data()
        else:
            logger.warning("Services not initialized - database not available")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        logger.info("Server will continue without database support")


@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()


async def initialize_mock_data():
    """Initialize database with mock products if empty"""
    if not database.database:
        logger.info("Skipping mock data initialization - database not available")
        return

    from utils import get_product_service
    try:
        product_service = get_product_service()
        products = await product_service.get_products(limit=1)
        if not products:
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
            {
                "name": "DTF Powder Adhesive",
                "category": "supplies",
                "price": 24.99,
                "image": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400&h=400&fit=crop",
                "description": "Premium hot melt adhesive powder for DTF transfers. 1lb container.",
                "features": ["1lb container", "Easy application", "Strong adhesion", "Washable"],
                "sizes": ["1lb"],
                "min_quantity": 1,
                "max_quantity": 50,
                "inventory": 75,
                "status": "active"
            },
            {
                "name": "Teflon Sheets (Pack of 5)",
                "category": "accessories",
                "price": 15.99,
                "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop",
                "description": "High-quality teflon sheets for heat pressing. Reusable and non-stick.",
                "features": ["Pack of 5", "Non-stick surface", "Reusable", "Heat resistant"],
                "sizes": ["16x20"],
                "min_quantity": 1,
                "max_quantity": 20,
                "inventory": 100,
                "status": "active"
            },
            {
                "name": "Custom Design Service",
                "category": "custom-designs",
                "price": 49.99,
                "image": "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=400&h=400&fit=crop",
                "description": "Professional custom design service. Our team creates unique designs for your brand.",
                "features": ["Professional design", "Unlimited revisions", "Commercial license", "48hr turnaround"],
                "sizes": ["Custom"],
                "min_quantity": 1,
                "max_quantity": 10,
                "inventory": 50,
                "status": "active"
            }
        ]

        from models.product import ProductCreate
        for product_data in mock_products:
            product = ProductCreate(**product_data)
            await product_service.create_product(product)

        logger.info("Mock product data initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize mock data: {e}")
