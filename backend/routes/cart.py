from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from models.cart import Cart, CartItemCreate, CartItemUpdate
from utils import get_cart_service

router = APIRouter(prefix="/cart", tags=["cart"])


def get_session_id(x_session_id: Optional[str] = Header(None)) -> str:
    """Get session ID from header or generate default"""
    return x_session_id or "default_session"


@router.get("/", response_model=Cart)
async def get_cart(session_id: str = Header(None, alias="x-session-id")):
    """Get current cart"""
    session_id = session_id or "default_session"
    return await get_cart_service().get_cart(session_id)


@router.post("/items", response_model=Cart)
async def add_item_to_cart(
    item: CartItemCreate,
    session_id: str = Header(None, alias="x-session-id")
):
    """Add item to cart"""
    session_id = session_id or "default_session"
    cart = await get_cart_service().add_item_to_cart(session_id, item)
    if not cart:
        raise HTTPException(status_code=400, detail="Unable to add item to cart")
    return cart


@router.put("/items/{item_index}", response_model=Cart)
async def update_cart_item(
    item_index: int,
    update_data: CartItemUpdate,
    session_id: str = Header(None, alias="x-session-id")
):
    """Update cart item quantity"""
    session_id = session_id or "default_session"
    cart = await get_cart_service().update_cart_item(session_id, item_index, update_data)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return cart


@router.delete("/items/{item_index}", response_model=Cart)
async def remove_cart_item(
    item_index: int,
    session_id: str = Header(None, alias="x-session-id")
):
    """Remove item from cart"""
    session_id = session_id or "default_session"
    cart = await get_cart_service().remove_cart_item(session_id, item_index)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return cart


@router.delete("/clear", response_model=Cart)
async def clear_cart(session_id: str = Header(None, alias="x-session-id")):
    """Clear all items from cart"""
    session_id = session_id or "default_session"
    return await get_cart_service().clear_cart(session_id)


@router.get("/summary")
async def get_cart_summary(session_id: str = Header(None, alias="x-session-id")):
    """Get cart summary with totals"""
    session_id = session_id or "default_session"
    cart = await get_cart_service().get_cart(session_id)
    
    return {
        "total_items": cart.get_total_items(),
        "subtotal": cart.get_subtotal(),
        "shipping": cart.get_shipping_cost(),
        "tax": cart.get_tax(),
        "total": cart.get_order_total(),
        "free_shipping_threshold": 75.0,
        "free_shipping_remaining": max(0, 75.0 - cart.get_subtotal())
    }