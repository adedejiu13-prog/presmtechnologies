import os
import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from services.database import get_products_collection, get_carts_collection

logger = logging.getLogger("shopify")
logging.basicConfig(level=logging.INFO)

class ShopifyService:
    """Handles Shopify GraphQL operations for products and checkout."""

    def __init__(self):
        self.store = os.getenv("SHOPIFY_STORE", "presmtechnologies.myshopify.com")
        self.token = os.getenv("SHOPIFY_STOREFRONT_TOKEN", "")
        self.graphql_url = f"https://{self.store}/api/2024-10/graphql.json"

        if not self.token:
            logger.warning("⚠️ SHOPIFY_STOREFRONT_TOKEN not set!")
        else:
            logger.info(f"✓ Shopify initialized for store: {self.store}")

    def _headers(self) -> Dict[str, str]:
        return {
            "X-Shopify-Storefront-Access-Token": self.token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def get_products_with_variants(self) -> Dict[str, Any]:
        """Fetch Shopify products with variants and sync to MongoDB."""
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
                    node { url }
                  }
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
                    self.graphql_url,
                    headers=self._headers(),
                    json={"query": query},
                    timeout=20.0,
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

            # Sync products to MongoDB
            try:
                products_col = get_products_collection()
                synced_count = 0
                for product in products:
                    product_dict = {
                        "shopify_id": product["id"],  # Fixed: Use "shopify_id" instead of "id"
                        "name": product["title"],
                        "category": "dtf-transfers",
                        "price": float(product["variants"][0]["price"]) if product["variants"] else 0.0,
                        "image": product["images"][0] if product["images"] else "",
                        "images": product["images"],
                        "description": product["description"],
                        "features": [],
                        "sizes": [v["title"] for v in product["variants"]],
                        "min_quantity": 1,
                        "max_quantity": 1000,
                        "inventory": 100,
                        "status": "active",
                        "variants": [
                            {
                                "shopify_id": v["id"],
                                "title": v["title"],
                                "price": float(v["price"]),
                                "available": v["available"]
                            } for v in product["variants"]
                        ],
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    logger.info(f"Attempting to sync product: {product_dict['shopify_id']}")
                    result = await products_col.update_one(
                        {"shopify_id": product_dict["shopify_id"]},
                        {"$set": product_dict},
                        upsert=True
                    )
                    logger.info(f"Synced product {product_dict['shopify_id']}: matched={result.matched_count}, modified={result.modified_count}, upserted={result.upserted_id}")
                    synced_count += 1
                logger.info(f"Successfully synced {synced_count} products to MongoDB")
            except Exception as e:
                logger.error(f"Failed to sync products to MongoDB: {str(e)}")
                raise

            return {"count": len(products), "products": products}

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching Shopify products: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error fetching Shopify products: {str(e)}")
            raise

    async def create_checkout(self, session_id: str) -> Dict[str, Any]:
        """Create a Shopify checkout from cart data in MongoDB."""
        try:
            carts_col = get_carts_collection()
            cart = await carts_col.find_one({"session_id": session_id})

            if not cart or not cart.get("items"):
                logger.error(f"Cart not found or empty for session: {session_id}")
                raise ValueError("Cart is empty or not found")

            line_items = []
            for item in cart["items"]:
                if not item.get("variant_id"):
                    logger.error(f"Missing variant_id for item: {item}")
                    raise ValueError(f"Missing variant_id for {item}")
                line_items.append({
                    "variantId": item["variant_id"],
                    "quantity": item.get("quantity", 1)
                })

            query = """
            mutation checkoutCreate($input: CheckoutCreateInput!) {
              checkoutCreate(input: $input) {
                checkout { id webUrl }
                checkoutUserErrors { message }
              }
            }
            """

            payload = {"query": query, "variables": {"input": {"lineItems": line_items}}}

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.graphql_url,
                    headers=self._headers(),
                    json=payload,
                    timeout=20.0,
                )
                response.raise_for_status()
                data = response.json()

            checkout = (
                data.get("data", {})
                .get("checkoutCreate", {})
                .get("checkout")
            )

            if not checkout:
                errors = (
                    data.get("data", {})
                    .get("checkoutCreate", {})
                    .get("checkoutUserErrors", [])
                )
                message = errors[0]["message"] if errors else "Checkout creation failed"
                logger.error(f"Checkout creation failed: {message}")
                raise ValueError(message)

            logger.info(f"Checkout created successfully: {checkout['id']}")
            return {"checkout_url": checkout["webUrl"], "checkout_id": checkout["id"]}

        except ValueError as e:
            logger.error(f"ValueError during checkout creation: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during checkout creation: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error during checkout creation: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))