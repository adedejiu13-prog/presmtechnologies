from fastapi import APIRouter, UploadFile, Form, HTTPException, Request
import requests
import os
import logging
import base64
import time
from dotenv import load_dotenv
from services.cart_service import get_cart_service

router = APIRouter(prefix="/api/shopify", tags=["gang_sheets"])

# ------------------------------
# Logging setup
# ------------------------------
logger = logging.getLogger("backend.gang_sheets")
logger.setLevel(logging.DEBUG)

# ------------------------------
# Load environment variables
# ------------------------------
load_dotenv()
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

if not SHOPIFY_ACCESS_TOKEN or not SHOPIFY_STORE:
    raise RuntimeError("Shopify credentials missing in .env")

SHOPIFY_API_URL = f"https://{SHOPIFY_STORE}/admin/api/2025-01/graphql.json"

# ------------------------------
# Helper: Convert Admin → Storefront ID
# ------------------------------
def admin_to_storefront_id(admin_id: str) -> str:
    if not admin_id:
        return None
    numeric_id = admin_id.split("/")[-1]
    return base64.b64encode(f"gid://shopify/ProductVariant/{numeric_id}".encode("utf-8")).decode("utf-8")

# ------------------------------
# Create Gang Sheet Endpoint
# ------------------------------
@router.post("/create-gang-sheet")
async def create_custom_gang_sheet(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = None,
    quantity: int = Form(1)
):
    """
    Creates a Shopify product (with default variant), attaches an image,
    fetches storefront variant ID, and optionally adds to cart.
    """
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
    }

    # ------------------------------
    # Step 1: Create Product
    # ------------------------------
    product_mutation = """
    mutation CreateProduct($input: ProductInput!) {
      productCreate(input: $input) {
        product { id title handle status }
        userErrors { field message }
      }
    }
    """
    product_variables = {
        "input": {
            "title": name,
            "descriptionHtml": description,
            "productType": "Gang Sheet",
            "status": "ACTIVE"
        }
    }
    product_response = requests.post(
        SHOPIFY_API_URL,
        headers=headers,
        json={"query": product_mutation, "variables": product_variables}
    )
    product_data = product_response.json()
    logger.debug(f"🧾 Shopify Product Create: {product_data}")

    if "errors" in product_data or product_data["data"]["productCreate"]["userErrors"]:
        raise HTTPException(status_code=400, detail="Error creating Shopify product")

    product = product_data["data"]["productCreate"]["product"]
    product_id = product["id"]
    product_handle = product["handle"]

    # ------------------------------
    # Step 2: Upload Image via ImgBB + attach to Shopify
    # ------------------------------
    image_url = None
    if image:
        try:
            if not IMGBB_API_KEY:
                raise HTTPException(status_code=500, detail="ImgBB API key not found")

            image_bytes = await image.read()
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")

            # Upload to ImgBB
            imgbb_res = requests.post(
                "https://api.imgbb.com/1/upload",
                params={"key": IMGBB_API_KEY},
                data={"image": encoded_image}
            )
            imgbb_data = imgbb_res.json()
            logger.debug(f"🖼️ ImgBB Upload Response: {imgbb_data}")

            if not imgbb_data.get("success"):
                raise HTTPException(status_code=400, detail="ImgBB upload failed")

            image_url = imgbb_data["data"]["url"]

            # Attach image to Shopify product
            media_mutation = """
            mutation productCreateMedia($productId: ID!, $media: [CreateMediaInput!]!) {
              productCreateMedia(productId: $productId, media: $media) {
                media { alt mediaContentType status preview { image { originalSrc } } }
                userErrors { field message }
              }
            }
            """
            media_variables = {
                "productId": product_id,
                "media": [{"alt": f"{name} image", "mediaContentType": "IMAGE", "originalSource": image_url}]
            }
            media_response = requests.post(
                SHOPIFY_API_URL, headers=headers, json={"query": media_mutation, "variables": media_variables}
            )
            media_data = media_response.json()
            logger.debug(f"🖼️ Shopify Media Upload: {media_data}")

            if "errors" in media_data or media_data["data"]["productCreateMedia"]["userErrors"]:
                raise HTTPException(status_code=400, detail="Shopify media upload failed")

            time.sleep(2)  # wait to ensure the image propagates

        except Exception as e:
            logger.error("❌ Error uploading image or attaching media", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    # ------------------------------
    # Step 3: Fetch default variant
    # ------------------------------
    try:
        variant_query = f"""
        {{
          product(id: "{product_id}") {{
            variants(first: 1) {{
              edges {{
                node {{ id price title }}
              }}
            }}
          }}
        }}
        """
        variant_response = requests.post(SHOPIFY_API_URL, headers=headers, json={"query": variant_query})
        variant_data = variant_response.json()
        logger.debug(f"🧬 Variant Fetch: {variant_data}")

        variant_id = (
            variant_data.get("data", {})
            .get("product", {})
            .get("variants", {})
            .get("edges", [{}])[0]
            .get("node", {})
            .get("id")
        )
        if not variant_id:
            raise HTTPException(status_code=400, detail="Variant ID not found")

        storefront_variant_id = admin_to_storefront_id(variant_id)

    except Exception as e:
        logger.error("❌ Error fetching variant ID", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    # ------------------------------
    # Step 4: Add to cart if session_id provided
    # ------------------------------
    session_id = request.headers.get("x-session-id")
    cart_data = None
    if session_id:
        cart_service = get_cart_service()
        cart = await cart_service.add_item_to_cart(
            session_id,
            product_id,
            storefront_variant_id,
            quantity
        )
        cart_data = {
            "id": cart.id,
            "session_id": cart.session_id,
            "items": cart.items,
            "created_at": cart.created_at,
            "updated_at": cart.updated_at
        }

    # ------------------------------
    # Step 5: Return all data
    # ------------------------------
    return {
        "message": "✅ Product created successfully!",
        "product_id": product_id,
        "variant_id_admin": variant_id,
        "variant_id_storefront": storefront_variant_id,
        "price": price,
        "product_url": f"https://{SHOPIFY_STORE}/products/{product_handle}",
        "admin_url": f"https://{SHOPIFY_STORE}/admin/products/{product_id.split('/')[-1]}",
        "image_url": image_url,
        "cart": cart_data
    }
