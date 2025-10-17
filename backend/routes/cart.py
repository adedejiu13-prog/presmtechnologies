import os
import requests
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel
from services.cart_service import get_cart_service

router = APIRouter(prefix="/api/cart", tags=["cart"])

# --- Shopify configuration ---
SHOPIFY_STORE = "presmtechnologies.myshopify.com"
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

# --- Request Model ---
class AddToCartRequest(BaseModel):
    product_id: str
    variant_id: str
    quantity: int = 1

# --- Helper: verify product from Shopify ---
def fetch_shopify_product(product_id: str):
    """Fetch product info from Shopify to verify existence."""
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-10/products/{product_id}.json"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("product")
    return None

# --- Add item to cart ---
@router.post("/items")
async def add_to_cart(request: Request, body: AddToCartRequest):
    session_id = request.headers.get("x-session-id")
    if not session_id:
        raise HTTPException(status_code=400, detail="x-session-id header missing")

    # ✅ Verify product exists in Shopify
    product = fetch_shopify_product(body.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found in Shopify")

    # ✅ Add to local cart (DB or memory)
    cart_service = get_cart_service()
    cart = await cart_service.add_item_to_cart(
        session_id,
        body.product_id,
        body.variant_id,
        body.quantity
    )

    # ✅ Handle missing product or variant properly
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
        },
        "product_info": {
            "title": product.get("title"),
            "price": product.get("variants", [{}])[0].get("price"),
            "image": product.get("image", {}).get("src")
        }
    }

# --- Get all items in a cart ---
@router.get("/items/{session_id}")
async def get_cart_items(session_id: str):
    """Get all items for a given session's cart."""
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

# --- Clear all items in cart ---
@router.delete("/items/{session_id}")
async def clear_cart(session_id: str):
    """Clear all items from a user's cart."""
    cart_service = get_cart_service()
    cleared = await cart_service.clear_cart(session_id)
    return {"status": "success", "cleared": cleared}

# --- Debug route ---
@router.get("/debug/{session_id}")
async def debug_cart(session_id: str):
    """Debug endpoint to inspect current cart."""
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
