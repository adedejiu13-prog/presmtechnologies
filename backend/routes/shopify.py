from fastapi import APIRouter, HTTPException, Header, Request
from typing import Optional
import os
import hmac
import hashlib
import json
import base64
from services.cart_service import cart_service

router = APIRouter(prefix="/shopify", tags=["shopify"])

# Shopify configuration
SHOPIFY_WEBHOOK_SECRET = os.getenv("SHOPIFY_WEBHOOK_SECRET", "")


def verify_shopify_webhook(data: bytes, signature: str) -> bool:
    """Verify Shopify webhook signature"""
    if not SHOPIFY_WEBHOOK_SECRET:
        return True  # Skip verification in development
    
    expected_signature = base64.b64encode(
        hmac.new(
            SHOPIFY_WEBHOOK_SECRET.encode('utf-8'),
            data,
            digestmod=hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    return hmac.compare_digest(expected_signature, signature)


@router.post("/webhooks/order/created")
async def handle_order_created(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None)
):
    """Handle Shopify order created webhook"""
    body = await request.body()
    
    # Verify webhook signature
    if not verify_shopify_webhook(body, x_shopify_hmac_sha256 or ""):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    try:
        order_data = json.loads(body.decode('utf-8'))
        # Process the order data here
        # Update gang sheet statuses, send notifications, etc.
        
        return {"status": "success", "message": "Order processed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing webhook: {str(e)}")


@router.post("/webhooks/order/updated")
async def handle_order_updated(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None)
):
    """Handle Shopify order updated webhook"""
    body = await request.body()
    
    if not verify_shopify_webhook(body, x_shopify_hmac_sha256 or ""):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    try:
        order_data = json.loads(body.decode('utf-8'))
        # Process order updates
        
        return {"status": "success", "message": "Order update processed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing webhook: {str(e)}")


@router.post("/checkout/create")
async def create_shopify_checkout(
    session_id: str = Header(None, alias="x-session-id")
):
    """Create Shopify checkout from cart"""
    session_id = session_id or "default_session"
    cart = await cart_service.get_cart(session_id)
    
    if not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Mock Shopify checkout creation
    checkout_url = f"https://presmtechnologies.myshopify.com/checkout/mock"
    
    return {
        "checkout_url": checkout_url,
        "checkout_id": f"mock_checkout_{session_id}",
        "total": cart.get_order_total()
    }


@router.get("/store/info")
async def get_store_info():
    """Get Shopify store information"""
    return {
        "store_name": "PRESM Technologies",
        "store_url": "https://presmtechnologies.myshopify.com",
        "currency": "USD",
        "country": "US",
        "policies": {
            "shipping_policy": "Free shipping on orders over $75",
            "return_policy": "30-day return policy",
            "privacy_policy": "Your privacy is important to us"
        }
    }