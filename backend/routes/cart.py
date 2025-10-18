from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from services.cart_service import get_cart_service

router = APIRouter(prefix="/api/cart", tags=["cart"])

class AddToCartRequest(BaseModel):
    product_id: str
    variant_id: str
    quantity: int = 1


@router.post("/items")
async def add_to_cart(request: Request, body: AddToCartRequest):
    session_id = request.headers.get("x-session-id")
    if not session_id:
        raise HTTPException(status_code=400, detail="x-session-id header missing")

    cart_service = get_cart_service()
    cart = await cart_service.add_item_to_cart(
        session_id,
        body.product_id,
        body.variant_id,
        body.quantity
    )

    if cart is None:
        raise HTTPException(status_code=404, detail="Product or variant not found in database")

    return {
        "status": "success",
        "message": f"{body.quantity} item(s) added to cart",
        "cart": {
            "id": cart.id,
            "session_id": cart.session_id,
            "items": cart.items,
            "created_at": cart.created_at,
            "updated_at": cart.updated_at
        }
    }


@router.get("/items/{session_id}")
async def get_cart_items(session_id: str):
    cart_service = get_cart_service()
    cart = await cart_service.get_or_create_cart(session_id)
    return {
        "session_id": session_id,
        "cart": {
            "id": cart.id,
            "items": cart.items,
            "created_at": cart.created_at,
            "updated_at": cart.updated_at
        }
    }


@router.delete("/items/{session_id}")
async def clear_cart(session_id: str):
    cart_service = get_cart_service()
    cart = await cart_service.get_or_create_cart(session_id)
    cart.items = []
    cart.updated_at = cart.updated_at
    async with cart_service.get_cart_service() as session:
        session.add(cart)
        await session.flush()
        await session.commit()
    return {"status": "success", "message": "Cart cleared"}


@router.get("/debug/{session_id}")
async def debug_cart(session_id: str):
    cart_service = get_cart_service()
    cart = await cart_service.get_or_create_cart(session_id)
    return {
        "session_id": session_id,
        "cart": {
            "id": cart.id,
            "session_id": cart.session_id,
            "items": cart.items,
            "created_at": cart.created_at,
            "updated_at": cart.updated_at
        }
    }
