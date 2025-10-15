import os
import logging
import hmac
import hashlib
import base64
import json
from typing import List
from fastapi import APIRouter, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.cart_service import cart_service
import httpx
import requests

# Set up logging
logger = logging.getLogger("shopify")
logging.basicConfig(level=logging.INFO)

# Environment variables
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE", "presmtechnologies.myshopify.com")
SHOPIFY_STOREFRONT_TOKEN = os.getenv("SHOPIFY_STOREFRONT_TOKEN", "")
SHOPIFY_WEBHOOK_SECRET = os.getenv("SHOPIFY_WEBHOOK_SECRET", "")
FRONTEND_ORIGIN = "https://presmtechnologies.com"

# FastAPI router
router = APIRouter(prefix="/shopify")

# CORS middleware (should be added in main.py, but shown here for clarity)
def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[FRONTEND_ORIGIN],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Helper: Shopify GraphQL endpoint
SHOPIFY_GRAPHQL_URL = f"https://{SHOPIFY_STORE}/api/2023-10/graphql.json"

# Helper: Shopify Storefront API headers
def shopify_headers():
    return {
        "X-Shopify-Storefront-Access-Token": SHOPIFY_STOREFRONT_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

# ──────────────────────────────────────────────
# 🛍️ Get All Shopify Products
# ──────────────────────────────────────────────
@router.get("/products")
async def get_shopify_products():
    """
    Fetch all products from Shopify Storefront API
    """
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
              edges {
                node {
                  url
                }
              }
            }
            variants(first: 5) {
              edges {
                node {
                  id
                  title
                  price {
                    amount
                    currencyCode
                  }
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
                SHOPIFY_GRAPHQL_URL,
                headers=shopify_headers(),
                json={"query": query}
            )
        response.raise_for_status()
        data = response.json()
        products = []
        for edge in data.get("data", {}).get("products", {}).get("edges", []):
            node = edge["node"]
            images = [
                {
                    "src": img["node"]["url"],
                }
                for img in node.get("images", {}).get("edges", [])
            ]
            variants = [
                {
                    "id": v["node"]["id"],
                    "title": v["node"]["title"],
                    "price": v["node"]["price"]["amount"],
                    "currency": v["node"]["price"]["currencyCode"],
                    "available": v["node"]["availableForSale"],
                }
                for v in node.get("variants", {}).get("edges", [])
            ]
            products.append(
                {
                    "id": node["id"],
                    "title": node["title"],
                    "handle": node["handle"],
                    "description": node.get("description", ""),
                    "images": images,
                    "variants": variants,
                }
            )

        return {"count": len(products), "products": products}
    except Exception as e:
        logger.error(f"Error fetching Shopify products: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch products")


# ──────────────────────────────────────────────
# 🛒 Create Shopify Checkout (LIVE)
# ──────────────────────────────────────────────
class CartItem(BaseModel):
    variantId: str
    quantity: int


class CheckoutRequest(BaseModel):
    items: List[CartItem]


@router.post("/checkout/create")
async def create_shopify_checkout(
    request: Request,
    x_session_id: str = Header(None, alias="x-session-id")
):
    """
    Create a real Shopify checkout from the user's cart
    """
    session_id = x_session_id or "default_session"
    cart = await cart_service.get_cart(session_id)

    if not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Make sure all cart items have Shopify variant IDs
    line_items = []
    for item in cart.items:
        if not getattr(item, "variant_id", None):
            raise HTTPException(status_code=400, detail=f"Missing variant_id for {item.name}")
        line_items.append({
            "variantId": item.variant_id,
            "quantity": item.quantity
        })

    query = """
    mutation checkoutCreate($input: CheckoutCreateInput!) {
      checkoutCreate(input: $input) {
        checkout {
          id
          webUrl
        }
        checkoutUserErrors {
          message
        }
      }
    }
    """

    payload = {
        "query": query,
        "variables": {"input": {"lineItems": line_items}},
    }

    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Storefront-Access-Token": SHOPIFY_STOREFRONT_TOKEN,
    }

    res = requests.post(
        f"https://{SHOPIFY_STORE}/api/2024-10/graphql.json",
        headers=headers,
        json=payload,
    )

    response_json = res.json()

    if "errors" in response_json:
        raise HTTPException(status_code=400, detail=response_json["errors"])

    checkout = response_json["data"]["checkoutCreate"]["checkout"]
    if not checkout:
        raise HTTPException(status_code=400, detail="Checkout creation failed")

    return {
        "checkout_url": checkout["webUrl"],
        "checkout_id": checkout["id"],
    }


# ──────────────────────────────────────────────
# 🔐 Verify Shopify Webhook Signature
# ──────────────────────────────────────────────
def verify_shopify_webhook(data: bytes, signature: str) -> bool:
    if not SHOPIFY_WEBHOOK_SECRET:
        return True  # Skip in dev
    expected_signature = base64.b64encode(
        hmac.new(
            SHOPIFY_WEBHOOK_SECRET.encode("utf-8"),
            data,
            digestmod=hashlib.sha256
        ).digest()
    ).decode("utf-8")
    return hmac.compare_digest(expected_signature, signature)


# ──────────────────────────────────────────────
# 📦 Shopify Webhooks (Order Created / Updated)
# ──────────────────────────────────────────────
@router.post("/webhooks/order/created")
async def handle_order_created(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None)
):
    body = await request.body()
    if not verify_shopify_webhook(body, x_shopify_hmac_sha256 or ""):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        order_data = json.loads(body.decode("utf-8"))
        # You can log or handle order here:
        # - Update order status
        # - Send email notifications
        # - Sync with internal DB
        logger.info(f"Order created: {order_data}")
        return {"status": "success", "message": "Order processed"}
    except Exception as e:
        logger.error(f"Error processing order created webhook: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing webhook: {str(e)}")


@router.post("/webhooks/order/updated")
async def handle_order_updated(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None)
):
    body = await request.body()
    if not verify_shopify_webhook(body, x_shopify_hmac_sha256 or ""):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        order_data = json.loads(body.decode("utf-8"))
        # Handle order update logic
        logger.info(f"Order updated: {order_data}")
        return {"status": "success", "message": "Order update processed"}
    except Exception as e:
        logger.error(f"Error processing order updated webhook: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing webhook: {str(e)}")


# ──────────────────────────────────────────────
# 🏪 Store Info (Optional)
# ──────────────────────────────────────────────
@router.get("/store/info")
async def get_store_info():
    return {
        "store_name": "PRESM Technologies",
        "store_url": f"https://{SHOPIFY_STORE}",
        "currency": "USD",
        "country": "US",
        "policies": {
            "shipping_policy": "Free shipping on orders over $75",
            "return_policy": "30-day return policy",
            "privacy_policy": "Your privacy is important to us",
        },
    }
