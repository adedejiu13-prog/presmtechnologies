import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import asyncio
from sqlalchemy import select
from services.database import SessionLocal
from models.product import Product

SHOPIFY_STORE = "presmtechnologies.myshopify.com"
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")


async def sync_shopify_products():
    """Fetch all products from Shopify and store/update them in the local DB."""
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-10/products.json?limit=250"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    print("📦 Fetching products from Shopify...")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ Failed to fetch products:", response.text)
        return

    products = response.json().get("products", [])
    if not products:
        print("⚠️ No products found in Shopify store.")
        return

    async with SessionLocal() as session:
        async with session.begin():
            for p in products:
                result = await session.execute(select(Product).where(Product.shopify_id == str(p["id"])))
                existing = result.scalars().first()

                variants_data = [
                    {
                        "shopify_id": v["id"],
                        "title": v["title"],
                        "price": v["price"]
                    }
                    for v in p.get("variants", [])
                ]

                # ✅ Safely determine product price
                product_price = None
                if p.get("variants"):
                    product_price = p["variants"][0].get("price")

                if existing:
                    existing.name = p["title"]
                    existing.description = p.get("body_html", "")
                    existing.image = p.get("image", {}).get("src")
                    existing.variants = variants_data
                    existing.price = product_price or 0.00
                    print(f"🔁 Updated: {p['title']}")
                else:
                    product_obj = Product(
                        shopify_id=str(p["id"]),
                        name=p["title"],
                        description=p.get("body_html", ""),
                        image=p.get("image", {}).get("src"),
                        price=product_price or 0.00,  # ✅ fallback default
                        variants=variants_data
                    )
                    session.add(product_obj)
                    print(f"🆕 Added: {p['title']}")

        await session.commit()
        print(f"✅ Synced {len(products)} products from Shopify.")


if __name__ == "__main__":
    asyncio.run(sync_shopify_products())
