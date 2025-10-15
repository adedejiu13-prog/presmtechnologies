import os
import httpx
import logging
from typing import List, Dict, Any, Optional
from database import get_products_collection, get_carts_collection

logger = logging.getLogger("shopify")

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

    # ──────────────────────────────────────────────
    # 🛍️ Get all products
    # ──────────────────────────────────────────────
    async def get_products_with_variants(self) -> List[Dict[str, Any]]:
        """Fetch Shopify products with variants."""
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

        # Optional: cache or sync products in your MongoDB for faster load later
        try:
            products_col = get_products_collection()
            for product in products:
                await products_col.update_one(
                    {"id": product["id"]},
                    {"$set": product},
                    upsert=True
                )
        except Exception as e:
            logger.warning(f"⚠️ Could not sync products to MongoDB: {e}")

        return products

    # ──────────────────────────────────────────────
    # 🛒 Create checkout
    # ──────────────────────────────────────────────
    async def create_checkout(self, session_id: str) -> Dict[str, Any]:
        """Create a Shopify checkout from cart data in MongoDB."""
        carts_col = get_carts_collection()
        cart = await carts_col.find_one({"session_id": session_id})

        if not cart or not cart.get("items"):
            raise ValueError("Cart is empty or not found")

        line_items = []
        for item in cart["items"]:
            if not item.get("variant_id"):
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
            raise ValueError(message)

        return checkout
