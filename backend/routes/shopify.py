# routes/shopify.py
import os
import logging
import hmac
import hashlib
import base64
import json
from fastapi import APIRouter, Request, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.cart_service import cart_service
import httpx

# -------------------------------
# Logging setup
# -------------------------------
logger = logging.getLogger("shopify")
logging.basicConfig(level=logging.INFO)

# -------------------------------
# Environment variables
# -------------------------------
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE", "presmtechnologies.myshopify.com")
SHOPIFY_STOREFRONT_TOKEN = os.getenv("SHOPIFY_STOREFRONT_TOKEN", "")
SHOPIFY_WEBHOOK_SECRET = os.getenv("SHOPIFY_WEBHOOK_SECRET", "")

FRONTEND_ORIGIN = "https://presmtechnologies.com"
SHOPIFY_GRAPHQL_URL = f"https://{SHOPIFY_STORE}/api/2024-10/graphql.json"

if not SHOPIFY_STOREFRONT_TOKEN:
    logger.warning("⚠️ Shopify token not set. Checkout integration will not work.")
else:
    logger.info(f"✓ Shopify integration configured for store: {SHOPIFY_STORE}")

# -------------------------------
# FastAPI router
# -------------------------------
router = APIRouter(prefix="/shopify")

def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[FRONTEND_ORIGIN],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def shopify_headers():
    return {
        "X-Shopify-Storefront-Access-Token": SHOPIFY_STOREFRONT_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

# -------------------------------
# GET Shopify Products
# -------------------------------
@router.get("/products")
async def get_shopify_products():
    query = """
    {
      products(first: 20) {
        edges {
          node {
            id
            title
            handle
            description
            images(first: 3) {
              edges { node { url } }
            }
            variants(first: 5) {
              edges {
                node {
                  id
                  title
                  price { amount currencyCode }
                  availableForSale
                }
              }
            }
          }
        }
      }
    }
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                SHOPIFY_GRAPHQL_URL, headers=shopify_headers(), json={"query": query}
            )
        response.raise_for_status()
        data = response.json()
        products = [
            {
                "id": edge["node"]["id"],
                "title": edge["node"]["title"],
                "handle": edge["node"]["handle"],
                "description": edge["node"].get("description", ""),
                "images": [img["node"]["url"] for img in edge["node"]["images"]["edges"]],
                "variants": [
                    {
                        "id": v["node"]["id"],
                        "title": v["node"]["title"],
                        "price": v["node"]["price"]["amount"],
                        "currency": v["node"]["price"]["currencyCode"],
                        "available": v["node"]["availableForSale"],
                    }
                    for v in edge["node"]["variants"]["edges"]
                ],
            }
            for edge in data.get("data", {}).get("products", {}).get("edges", [])
        ]
        return {"count": len(products), "products": products}
    except Exception as e:
        logger.error(f"❌ Error fetching Shopify products: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch Shopify products")

# -------------------------------
# CREATE Shopify Checkout
# -------------------------------
@router.post("/checkout/create")
async def create_shopify_checkout(request: Request, x_session_id: str = Header(None, alias="x-session-id")):
    """Create a Shopify checkout from cart items"""
    try:
        data = await request.json()
    except Exception:
        data = {}

    session_id = x_session_id or data.get("session_id") or "default_session"
    logger.info(f"🧩 Creating checkout for session: {session_id}")

    if not SHOPIFY_STOREFRONT_TOKEN:
        raise HTTPException(status_code=503, detail="Shopify token not configured")

    # Fetch cart
    cart = await cart_service.get_cart(session_id)
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Prepare line items for Shopify
    line_items = []
    for item in cart.items:
        variant_id = getattr(item, "variant_id", None)
        if not variant_id:
            logger.warning(f"Item {item.name} missing variant_id, skipping...")
            continue
        line_items.append({"variantId": variant_id, "quantity": item.quantity})

    if not line_items:
        raise HTTPException(status_code=400, detail="No valid items with variant_id in cart")

    # Shopify GraphQL mutation
    query = """
    mutation checkoutCreate($input: CheckoutCreateInput!) {
      checkoutCreate(input: $input) {
        checkout { id webUrl }
        checkoutUserErrors { message }
      }
    }
    """
    payload = {"query": query, "variables": {"input": {"lineItems": line_items}}}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SHOPIFY_GRAPHQL_URL, headers=shopify_headers(), json=payload)
        response.raise_for_status()
        res_json = response.json()
        checkout = res_json.get("data", {}).get("checkoutCreate", {}).get("checkout")
        if not checkout:
            errors = res_json.get("data", {}).get("checkoutCreate", {}).get("checkoutUserErrors", [])
            raise HTTPException(status_code=400, detail=errors[0]["message"] if errors else "Checkout creation failed")
        logger.info(f"✅ Checkout created: {checkout['webUrl']}")
        return {"checkout_url": checkout["webUrl"], "checkout_id": checkout["id"]}
    except httpx.HTTPError as e:
        logger.error(f"HTTP error during Shopify checkout: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------
# Shopify Webhooks
# -------------------------------
def verify_shopify_webhook(data: bytes, signature: str) -> bool:
    if not SHOPIFY_WEBHOOK_SECRET:
        return True
    expected = base64.b64encode(hmac.new(SHOPIFY_WEBHOOK_SECRET.encode(), data, hashlib.sha256).digest()).decode()
    return hmac.compare_digest(expected, signature)

@router.post("/webhooks/order/created")
async def webhook_order_created(request: Request, x_shopify_hmac_sha256: str = Header(None)):
    body = await request.body()
    if not verify_shopify_webhook(body, x_shopify_hmac_sha256 or ""):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    try:
        order = json.loads(body)
        logger.info(f"🧾 Shopify order created: {order}")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhooks/order/updated")
async def webhook_order_updated(request: Request, x_shopify_hmac_sha256: str = Header(None)):
    body = await request.body()
    if not verify_shopify_webhook(body, x_shopify_hmac_sha256 or ""):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    try:
        order = json.loads(body)
        logger.info(f"🔁 Shopify order updated: {order}")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# -------------------------------
# Debug Endpoint
# -------------------------------
@router.get("/debug")
async def debug_shopify():
    token = os.getenv("SHOPIFY_STOREFRONT_TOKEN")
    return {
        "SHOPIFY_STORE": SHOPIFY_STORE,
        "SHOPIFY_STOREFRONT_TOKEN": (token[:6] + "..." if token else None)
    }
