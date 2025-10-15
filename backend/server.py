# backend/server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from pathlib import Path
import logging

# -------------------------------
# Environment Setup
# -------------------------------
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")

# -------------------------------
# Logging
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("backend")

# -------------------------------
# FastAPI App
# -------------------------------
app = FastAPI(
    title="PRESM Backend API",
    description="Backend API for PRESM Technologies DTF transfer platform",
    version="1.0.0"
)

# -------------------------------
# CORS
# -------------------------------
FRONTEND_ORIGINS = [
    "https://presmtechnologies.com",
    "https://www.presmtechnologies.com",
    "http://localhost:3000",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Include Routers (after app exists!)
# -------------------------------
from routes import cart, shopify
app.include_router(cart.router, prefix="/api/cart")      # <-- THIS
app.include_router(shopify.router, prefix="/api")

# -------------------------------
# MongoDB Connection
# -------------------------------
from services.database import connect_to_mongo, close_mongo_connection

@app.on_event("startup")
async def startup_event():
    try:
        await connect_to_mongo()
        logger.info("✅ Connected to MongoDB")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
    logger.info("🧹 MongoDB connection closed")

# -------------------------------
# React frontend (optional)
# -------------------------------
FRONTEND_BUILD_PATH = ROOT_DIR / "frontend" / "build"
if FRONTEND_BUILD_PATH.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_BUILD_PATH / "static")), name="static")

    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        file_path = FRONTEND_BUILD_PATH / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_BUILD_PATH / "index.html")

# -------------------------------
# Health
# -------------------------------
@app.get("/")
async def root():
    return {"message": "Backend running successfully!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
@app.get("/debug/db")
async def debug_db():
    from services.database import database
    if database.database is None:
        return {"status": "error", "detail": "Database not initialized"}
    try:
        await database.database.command("ping")
        return {"status": "success", "detail": "Database connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}