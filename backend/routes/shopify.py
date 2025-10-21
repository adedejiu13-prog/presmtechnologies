import os
import logging
from typing import Any, Dict, List

import httpx
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from services.database import SessionLocal
from models.product import Product

# ========== SETUP ==========
logger = logging.getLogger("shopify")
logging.basicConfig(level=logging.INFO)

SHOPIFY_STORE = os.getenv("SHOPIFY_STORE", "presmtechnologies.myshopify.com")
SHOPIFY_STOREFRONT_TOKEN = os.getenv("SHOPIFY_STOREFRONT_TOKEN", "")
SHOPIFY_GRAPHQL_URL = f"https://{SHOPIFY_STORE}/api/2024-10/graphql.json"

if not SHOPIFY_STOREFRONT_TOKEN:
    logger.warning("⚠️ Shopify token not set. Sync will not work.")
else:
    logger.info(f"✅ Shopify integration configured for store: {SHOPIFY_STORE}")

router = APIRouter(prefix="/shopify", tags=["Shopify"])

# Helper for headers
def shopify_headers() -> Dict[str, str]:
    return {
        "X-Shopify-Storefront-Access-Token": SHOPIFY_STOREFRONT_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

# =====================================================
# 🛍️  GET PRODUCTS
# =====================================================
@router.get("/products")
async def get_shopify_products() -> Dict[str, Any]:
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
                  priceV2 { amount currencyCode }
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
                SHOPIFY_GRAPHQL_URL, headers=shopify_headers(), json={"query": query}, timeout=20.0
            )

        if response.status_code >= 400:
            logger.error("Shopify products HTTP %s: %s", response.status_code, response.text)
            raise HTTPException(status_code=502, detail="Shopify API error")

        data = response.json()
        if "errors" in data:
            logger.error("Shopify GraphQL errors: %s", data.get("errors"))
            raise HTTPException(status_code=502, detail="Shopify GraphQL error")

        product_edges = data.get("data", {}).get("products", {}).get("edges", [])
        products: List[Dict[str, Any]] = []

        for edge in product_edges:
            node = edge.get("node", {})
            images = [img["node"]["url"] for img in node.get("images", {}).get("edges", [])]
            variants = [
                {
                    "shopify_id": v["node"]["id"],
                    "title": v["node"]["title"],
                    "price": float(v["node"]["priceV2"]["amount"]),
                    "available": v["node"]["availableForSale"],
                }
                for v in node.get("variants", {}).get("edges", [])
            ]
            products.append(
                {
                    "shopify_id": node["id"],
                    "name": node["title"],
                    "description": node.get("description", ""),
                    "price": variants[0]["price"] if variants else 0.0,
                    "image": images[0] if images else None,
                    "images": images,
                    "variants": variants,
                }
            )

        # Save or update DB records
        async with SessionLocal() as session:
            async with session.begin():
                for p in products:
                    result = await session.execute(select(Product).where(Product.shopify_id == p["shopify_id"]))
                    existing = result.scalars().first()
                    if existing:
                        existing.name = p["name"]
                        existing.description = p["description"]
                        existing.price = p["price"]
                        existing.image = p["image"]
                        existing.images = p["images"]
                        existing.variants = p["variants"]
                    else:
                        new = Product(
                            shopify_id=p["shopify_id"],
                            name=p["name"],
                            description=p["description"],
                            price=p["price"],
                            image=p["image"],
                            images=p["images"],
                            variants=p["variants"],
                        )
                        session.add(new)

        return {"count": len(products), "products": products}

    except Exception as e:
        logger.exception("Error fetching Shopify products")
        raise HTTPException(status_code=500, detail=f"Failed to fetch products: {e}")

# =====================================================
# 🛒  CREATE CART (replaces old checkout)
# =====================================================
# =====================================================
# 🛒  CREATE CART (supports multiple items)
# =====================================================
@router.post("/cart/create")
async def create_cart(payload: dict) -> Dict[str, Any]:
    """Creates a Shopify cart with one or more items and returns the checkout URL."""
    if not SHOPIFY_STOREFRONT_TOKEN:
        raise HTTPException(status_code=503, detail="Shopify token not configured")

    # ✅ Support both single and multiple items
    items = payload.get("items")
    if items and isinstance(items, list):
        # Multiple products format
        line_items = [
            {"quantity": item.get("quantity", 1), "merchandiseId": item["variant_id"]}
            for item in items
            if "variant_id" in item
        ]
    else:
        # Single product fallback
        variant_id = payload.get("variant_id")
        quantity = payload.get("quantity", 1)
        if not variant_id:
            raise HTTPException(status_code=400, detail="variant_id or items[] is required")
        line_items = [{"quantity": quantity, "merchandiseId": variant_id}]

    query = """
    mutation cartCreate($input: CartInput!) {
      cartCreate(input: $input) {
        cart {
          id
          checkoutUrl
        }
        userErrors {
          field
          message
        }
      }
    }
    """

    variables = {
        "input": {
            "lines": line_items
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                SHOPIFY_GRAPHQL_URL,
                headers=shopify_headers(),
                json={"query": query, "variables": variables},
                timeout=20.0,
            )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()
        logger.info("🛒 Shopify cartCreate response: %s", data)

        user_errors = data.get("data", {}).get("cartCreate", {}).get("userErrors", [])
        if user_errors:
            raise HTTPException(status_code=400, detail=user_errors)

        cart = data.get("data", {}).get("cartCreate", {}).get("cart", {})
        if not cart or not cart.get("checkoutUrl"):
            raise HTTPException(status_code=500, detail="Cart creation failed: no checkoutUrl")

        return {"checkout_url": cart["checkoutUrl"], "cart_id": cart["id"]}

    except Exception as e:
        logger.exception("Error creating cart")
        raise HTTPException(status_code=500, detail=f"Cart creation failed: {str(e)}")
