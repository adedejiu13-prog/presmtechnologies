from fastapi import APIRouter, Header, HTTPException, Body
from typing import List
from models.cart import Cart, CartItemCreate, CartItemUpdate
from services.cart_service import get_cart_service
import logging

logger = logging.getLogger("cart_routes")
logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.get("/", response_model=Cart)
async def get_cart(x_session_id: str = Header(..., alias="x-session-id")):
    try:
        cart_service = get_cart_service()
        cart = await cart_service.get_cart(x_session_id)
        logger.info(f"Retrieved cart for session: {x_session_id}")
        return cart
    except Exception as e:
        logger.error(f"Error retrieving cart for session {x_session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve cart: {str(e)}")

@router.post("/items", response_model=Cart)
async def add_cart_item(item: CartItemCreate = Body(...), x_session_id: str = Header(..., alias="x-session-id")):
    try:
        cart_service = get_cart_service()
        updated_cart = await cart_service.add_item_to_cart(x_session_id, item)
        if not updated_cart:
            logger.error(f"Failed to add item to cart for session {x_session_id}: {item}")
            raise HTTPException(status_code=404, detail="Item not found or invalid")
        logger.info(f"Added item to cart for session: {x_session_id}")
        return updated_cart
    except Exception as e:
        logger.error(f"Error adding item to cart for session {x_session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add item to cart: {str(e)}")

@router.put("/items/{item_index}", response_model=Cart)
async def update_cart_item(item_index: int, update: CartItemUpdate = Body(...), x_session_id: str = Header(..., alias="x-session-id")):
    try:
        cart_service = get_cart_service()
        updated_cart = await cart_service.update_cart_item(x_session_id, item_index, update)
        if not updated_cart:
            logger.error(f"Failed to update item at index {item_index} for session {x_session_id}")
            raise HTTPException(status_code=404, detail="Item not found")
        logger.info(f"Updated item at index {item_index} for session: {x_session_id}")
        return updated_cart
    except Exception as e:
        logger.error(f"Error updating item at index {item_index} for session {x_session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update cart item: {str(e)}")

@router.delete("/items/{item_index}", response_model=Cart)
async def remove_cart_item(item_index: int, x_session_id: str = Header(..., alias="x-session-id")):
    try:
        cart_service = get_cart_service()
        updated_cart = await cart_service.remove_cart_item(x_session_id, item_index)
        if not updated_cart:
            logger.error(f"Failed to remove item at index {item_index} for session {x_session_id}")
            raise HTTPException(status_code=404, detail="Item not found")
        logger.info(f"Removed item at index {item_index} for session: {x_session_id}")
        return updated_cart
    except Exception as e:
        logger.error(f"Error removing item at index {item_index} for session {x_session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to remove cart item: {str(e)}")

@router.delete("/", response_model=Cart)
async def clear_cart(x_session_id: str = Header(..., alias="x-session-id")):
    try:
        cart_service = get_cart_service()
        cleared_cart = await cart_service.clear_cart(x_session_id)
        logger.info(f"Cleared cart for session: {x_session_id}")
        return cleared_cart
    except Exception as e:
        logger.error(f"Error clearing cart for session {x_session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cart: {str(e)}")