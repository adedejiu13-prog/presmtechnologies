from fastapi import APIRouter, HTTPException
import requests
import os
import logging
from dotenv import load_dotenv

router = APIRouter(prefix="/api/shopify", tags=["gang_sheets"])

logger = logging.getLogger("backend.gang_sheets")
logger.setLevel(logging.DEBUG)

load_dotenv()
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE", "presmtechnologies.myshopify.com")

SHOPIFY_ADMIN_URL = f"https://{SHOPIFY_STORE}/admin/api/2024-10/graphql.json"


@router.post("/create-gang-sheet")
async def create_custom_gang_sheet(data: dict):
    """
    Stepwise creation of a Shopify product with variant + image (2024-10 API compliant)
    """
    try:
        name = data.get("name", "Custom Gang Sheet")
        description = data.get("description", "")
        price = data.get("price", 0)
        image_url = data.get("image_url")

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        }

        # STEP 1 — Create product (no variants or images)
        product_create_query = """
        mutation productCreate($input: ProductInput!) {
          productCreate(input: $input) {
            product { id title handle }
            userErrors { field message }
          }
        }
        """

        product_variables = {
            "input": {
                "title": name,
                "descriptionHtml": description,
                "status": "ACTIVE",
            }
        }

        product_res = requests.post(
            SHOPIFY_ADMIN_URL,
            headers=headers,
            json={"query": product_create_query, "variables": product_variables},
        )
        product_data = product_res.json()
        logger.debug(f"🧾 Product creation response: {product_data}")

        if "errors" in product_data:
            raise HTTPException(status_code=400, detail=product_data["errors"])

        user_errors = product_data["data"]["productCreate"]["userErrors"]
        if user_errors:
            raise HTTPException(status_code=400, detail=user_errors)

        product = product_data["data"]["productCreate"]["product"]
        product_id = product["id"]

        # STEP 2 — Create variant (corrected for API 2024-10)
variant_query = """
mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkCreate(productId: $productId, variants: $variants) {
    productVariants {
      id
      title
      price
    }
    userErrors {
      field
      message
    }
  }
}
"""

variant_variables = {
    "productId": product_id,
    "variants": [
        {
            "price": str(price),
            "optionValues": ["Default"]   # ✅ Correct field name
        }
    ]
}



        # STEP 3 — Attach image
        if image_url:
            media_query = """
            mutation productCreateMedia($productId: ID!, $media: [CreateMediaInput!]!) {
              productCreateMedia(productId: $productId, media: $media) {
                media { id image { url } }
                userErrors { field message }
              }
            }
            """

            media_variables = {
                "productId": product_id,
                "media": [
                    {
                        "mediaContentType": "IMAGE",
                        "originalSource": image_url
                    }
                ],
            }

            media_res = requests.post(
                SHOPIFY_ADMIN_URL,
                headers=headers,
                json={"query": media_query, "variables": media_variables},
            )
            media_data = media_res.json()
            logger.debug(f"🧾 Media upload response: {media_data}")

            if "errors" in media_data:
                raise HTTPException(status_code=400, detail=media_data["errors"])

            media_errors = media_data["data"]["productCreateMedia"]["userErrors"]
            if media_errors:
                raise HTTPException(status_code=400, detail=media_errors)

        # ✅ SUCCESS RESPONSE
        return {
            "status": "success",
            "product_id": product_id,
            "title": name,
            "price": price,
            "image": image_url,
            "shopify_product_url": f"https://{SHOPIFY_STORE}/products/{product['handle']}"
        }

    except Exception as e:
        logger.exception("Error creating gang sheet product")
        raise HTTPException(status_code=500, detail=str(e))
