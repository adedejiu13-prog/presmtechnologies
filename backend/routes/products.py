from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models.product import Product, ProductCreate, ProductUpdate
from utils import get_product_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=List[Product])
async def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of products to return")
):
    """Get all products with optional filtering"""
    if search:
        return await get_product_service().search_products(search, category)
    return await get_product_service().get_products(category, skip=skip, limit=limit)


@router.get("/categories")
async def get_categories():
    """Get all product categories with counts"""
    return await get_product_service().get_categories()


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a specific product by ID"""
    product = await get_product_service().get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=Product)
async def create_product(product: ProductCreate):
    """Create a new product (admin only)"""
    return await get_product_service().create_product(product)


@router.put("/{product_id}", response_model=Product)
async def update_product(product_id: str, product: ProductUpdate):
    """Update a product (admin only)"""
    updated_product = await get_product_service().update_product(product_id, product)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product


@router.delete("/{product_id}")
async def delete_product(product_id: str):
    """Delete a product (admin only)"""
    success = await get_product_service().delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}