# backend/routes/gang_sheets.py
import os
import time
import base64
import asyncio
import logging
import requests
from datetime import datetime
from fastapi import APIRouter, UploadFile, Form, HTTPException, Request
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from services.database import SessionLocal
from services.cart_service import get_cart_service
from models.product import Product

# ------------------------------------------------------------------
# Setup
# ------------------------------------------------------------------
router = APIRouter(prefix="/api/shopify", tags=["gang_sheets"])
logger = logging.getLogger("backend.gang_sheets")
logger.setLevel(logging.DEBUG)

load_dotenv()
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STOREFRONT_TOKEN = os.getenv("SHOPIFY_STOREFRONT_TOKEN")
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
SHOPIFY_ONLINE_CHANNEL_ID = os.getenv("SHOPIFY_ONLINE_CHANNEL_ID")  # this should be a Publication GID (not channelId)

if not SHOPIFY_ACCESS_TOKEN or not SHOPIFY_STORE:
    raise RuntimeError("❌ Missing Shopify credentials in .env")

if not SHOPIFY_STOREFRONT_TOKEN:
    logger.warning("⚠️ SHOPIFY_STOREFRONT_TOKEN not set. cartCreate (checkout) will fail until provided.")

SHOPIFY_GRAPHQL_ADMIN = f"https://{SHOPIFY_STORE}/admin/api/2025-01/graphql.json"
SHOPIFY_GRAPHQL_STOREFRONT = f"https://{SHOPIFY_STORE}/api/2025-01/graphql.json"
SHOPIFY_REST_BASE = f"https://{SHOPIFY_STORE}/admin/api/2025-01"

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def numeric_id_from_gid(gid: str) -> str:
    return gid.split("/")[-1] if gid else None

def build_variant_gid_from_numeric(numeric_id: int) -> str:
    return f"gid://shopify/ProductVariant/{numeric_id}"

# ------------------------------------------------------------------
# DB upsert
# ------------------------------------------------------------------
async def upsert_product_local(shopify_gid: str, product_data: dict):
    async with SessionLocal() as db:
        try:
            result = await db.execute(select(Product).where(Product.shopify_id == shopify_gid))
            prod = result.scalars().first()
            if prod:
                prod.name = product_data.get("name", prod.name)
                prod.description = product_data.get("description", prod.description)
                prod.price = product_data.get("price", prod.price)
                prod.image = product_data.get("image", prod.image)
                prod.variants = product_data.get("variants", prod.variants)
                prod.updated_at = datetime.utcnow()
            else:
                prod = Product(
                    shopify_id=shopify_gid,
                    name=product_data.get("name"),
                    description=product_data.get("description", ""),
                    price=product_data.get("price", 0),
                    image=product_data.get("image"),
                    variants=product_data.get("variants", []),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(prod)
            await db.commit()
            await db.refresh(prod)
            logger.info(f"💾 Product upserted locally: {prod.name}")
            return prod
        except SQLAlchemyError as e:
            logger.error(f"❌ Database error in upsert_product_local: {e}")
            await db.rollback()
            return None

# ------------------------------------------------------------------
# ImgBB upload with retry
# ------------------------------------------------------------------
def upload_to_imgbb_with_retry(encoded_image: str, max_retries: int = 3, delay: int = 2) -> str:
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"🖼️ Uploading image to ImgBB (Attempt {attempt}/{max_retries})...")
            resp = requests.post(
                "https://api.imgbb.com/1/upload",
                params={"key": IMGBB_API_KEY},
                data={"image": encoded_image},
                timeout=20,
            )
            data = resp.json()
            if data.get("success"):
                logger.info("✅ ImgBB upload successful!")
                return data["data"]["url"]
            logger.warning(f"⚠️ ImgBB upload failed (attempt {attempt}): {data}")
        except Exception as e:
            logger.error(f"❌ ImgBB upload error (attempt {attempt}): {e}")
        if attempt < max_retries:
            time.sleep(delay)
    raise HTTPException(status_code=400, detail="Image upload failed after multiple retries.")

# ------------------------------------------------------------------
# Poll Storefront to confirm variant exists / is available
# ------------------------------------------------------------------
def wait_for_variant_in_storefront(variant_gid: str, timeout: int = 20, interval: int = 2) -> bool:
    """
    Poll the storefront API for the variant node to appear.
    Returns True if variant appears within timeout, False otherwise.
    """
    if not SHOPIFY_STOREFRONT_TOKEN:
        raise HTTPException(status_code=500, detail="Missing SHOPIFY_STOREFRONT_TOKEN for Storefront API.")

    query = """
    query nodeById($id: ID!) {
      node(id: $id) {
        ... on ProductVariant {
          id
          availableForSale
          product { id }
        }
      }
    }
    """
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Storefront-Access-Token": SHOPIFY_STOREFRONT_TOKEN,
    }
    end_at = time.time() + timeout
    attempt = 0
    while time.time() < end_at:
        attempt += 1
        try:
            logger.debug("Storefront node query attempt %s for %s", attempt, variant_gid)
            r = requests.post(SHOPIFY_GRAPHQL_STOREFRONT, json={"query": query, "variables": {"id": variant_gid}}, headers=headers, timeout=10)
            data = r.json()
            # If GraphQL returned errors, log but continue retry (transient possible).
            if "errors" in data:
                logger.debug("Storefront node errors: %s", data["errors"])
            node = data.get("data", {}).get("node")
            if node:
                logger.info("✅ Variant visible in Storefront: %s (availableForSale=%s)", node.get("id"), node.get("availableForSale"))
                return True
        except Exception as e:
            logger.debug("Storefront poll exception (ignored): %s", e)
        logger.info("Variant not yet visible in Storefront, waiting %s seconds...", interval)
        time.sleep(interval)
    logger.warning("Timed out waiting for variant to appear in Storefront.")
    return False

# ------------------------------------------------------------------
# Create Shopify cart (Storefront API) -> returns checkoutUrl
# ------------------------------------------------------------------
def create_shopify_checkout(variant_gid: str, quantity: int, max_retries: int = 2) -> str:
    if not SHOPIFY_STOREFRONT_TOKEN:
        raise HTTPException(status_code=500, detail="Missing SHOPIFY_STOREFRONT_TOKEN for Storefront API (cartCreate).")

    mutation = """
    mutation cartCreate($input: CartInput!) {
      cartCreate(input: $input) {
        cart { id checkoutUrl }
        userErrors { field message }
      }
    }
    """
    variables = {"input": {"lines": [{"quantity": quantity, "merchandiseId": variant_gid}]}}
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Storefront-Access-Token": SHOPIFY_STOREFRONT_TOKEN,
    }

    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            logger.info("🛒 Creating cart via Storefront API (attempt %s/%s)...", attempt, max_retries)
            r = requests.post(SHOPIFY_GRAPHQL_STOREFRONT, json={"query": mutation, "variables": variables}, headers=headers, timeout=20)
            data = r.json()
            if "errors" in data:
                last_err = data["errors"]
                logger.error("GraphQL errors from Storefront API: %s", last_err)
                # don't retry on client side errors like invalid GID -> raise
                raise HTTPException(status_code=400, detail=last_err)
            payload = data.get("data", {}).get("cartCreate", {})
            user_errors = payload.get("userErrors") or []
            if user_errors:
                last_err = user_errors
                logger.error("Storefront userErrors: %s", user_errors)
                raise HTTPException(status_code=400, detail=user_errors)
            cart = payload.get("cart")
            if cart and cart.get("checkoutUrl"):
                logger.info("✅ Checkout URL obtained: %s", cart["checkoutUrl"])
                return cart["checkoutUrl"]
            last_err = f"No checkoutUrl returned: {data}"
            logger.warning(last_err)
        except HTTPException:
            raise
        except Exception as e:
            last_err = str(e)
            logger.error("Error calling Storefront cartCreate: %s", e)
        if attempt < max_retries:
            time.sleep(2)
    raise HTTPException(status_code=500, detail=f"Failed to create checkout via Storefront API: {last_err}")

# ------------------------------------------------------------------
# Main endpoint
# ------------------------------------------------------------------
@router.post("/create-gang-sheet")
async def create_custom_gang_sheet(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = None,
    image_url: str = Form(None),
    quantity: int = Form(1),
):
    logger.info(f"🚀 Creating gang sheet '{name}' (${price}) qty={quantity}")

    headers_admin = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    }

    # 1) Create product (Admin GraphQL)
    mutation_create = """
    mutation CreateProduct($input: ProductInput!) {
      productCreate(input: $input) {
        product { id title handle status }
        userErrors { field message }
      }
    }
    """
    variables = {
        "input": {
            "title": name,
            "descriptionHtml": description,
            "productType": "Gang Sheet",
            "status": "ACTIVE",
        }
    }
    resp = requests.post(SHOPIFY_GRAPHQL_ADMIN, headers=headers_admin, json={"query": mutation_create, "variables": variables}, timeout=30)
    try:
        data = resp.json()
    except Exception:
        logger.exception("Failed to parse Shopify product create response")
        raise HTTPException(status_code=500, detail="Invalid response from Shopify product create")

    if "errors" in data:
        raise HTTPException(status_code=400, detail=data["errors"])

    product_payload = data.get("data", {}).get("productCreate", {})
    user_errors = product_payload.get("userErrors") or []
    if user_errors:
        raise HTTPException(status_code=400, detail=user_errors)

    product = product_payload.get("product")
    if not product:
        raise HTTPException(status_code=500, detail="Product not returned after creation")

    product_gid = product["id"]
    product_handle = product.get("handle")
    numeric_id = numeric_id_from_gid(product_gid)
    logger.info("✅ Product created on Shopify: %s", product_gid)

    # 2) Get or create variant
    v_query = f"""
    {{
      product(id: "{product_gid}") {{
        variants(first: 10) {{
          edges {{ node {{ id title price availableForSale }} }}
        }}
      }}
    }}
    """
    v_resp = requests.post(SHOPIFY_GRAPHQL_ADMIN, headers=headers_admin, json={"query": v_query}, timeout=20)
    try:
        v_data = v_resp.json()
    except Exception:
        logger.exception("Failed to parse Shopify variant query response")
        raise HTTPException(status_code=500, detail="Invalid response from Shopify variant query")

    edges = v_data.get("data", {}).get("product", {}).get("variants", {}).get("edges", [])
    variant_gid = edges[0]["node"]["id"] if edges else None

    if not variant_gid:
        rest_url = f"{SHOPIFY_REST_BASE}/products/{numeric_id}/variants.json"
        v_payload = {"variant": {"price": str(price), "option1": "Default Title"}}
        rest = requests.post(rest_url, headers={"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN}, json=v_payload, timeout=20)
        try:
            rest_json = rest.json()
        except Exception:
            logger.exception("Failed to parse REST variant create response")
            raise HTTPException(status_code=500, detail="Invalid response from Shopify variant create")
        variant_num = rest_json.get("variant", {}).get("id")
        if not variant_num:
            logger.error("Variant create returned unexpected payload: %s", rest_json)
            raise HTTPException(status_code=500, detail="Variant creation failed")
        variant_gid = build_variant_gid_from_numeric(variant_num)

    logger.info("✅ Variant ready: %s", variant_gid)

    # 3) Publish product to Online Store (publicationId)
    if SHOPIFY_ONLINE_CHANNEL_ID:
        publish_mutation = """
        mutation publishProductToChannel($productId: ID!, $publicationId: ID!) {
          publishablePublish(input: {id: $productId, publicationId: $publicationId}) {
            userErrors { field message }
          }
        }
        """
        pub_resp = requests.post(
            SHOPIFY_GRAPHQL_ADMIN,
            headers=headers_admin,
            json={
                "query": publish_mutation,
                "variables": {"productId": product_gid, "publicationId": SHOPIFY_ONLINE_CHANNEL_ID},
            },
            timeout=15,
        )
        try:
            pub_data = pub_resp.json()
        except Exception:
            logger.exception("Failed to parse publish response")
            pub_data = {}
        errs = pub_data.get("data", {}).get("publishablePublish", {}).get("userErrors")
        if errs:
            logger.warning("⚠️ Publish userErrors: %s", errs)
        else:
            logger.info("🌐 Product published to Online Store (publicationId=%s)", SHOPIFY_ONLINE_CHANNEL_ID)
        # short delay to let Shopify propagate
        time.sleep(3)
    else:
        logger.warning("No SHOPIFY_ONLINE_CHANNEL_ID provided; product may not be visible in storefront.")

    # 4) Image upload
    image_url_final = None
    image_bytes = None
    if image_url and not image:
        try:
            img_resp = requests.get(image_url, timeout=10)
            img_resp.raise_for_status()
            image_bytes = img_resp.content
        except Exception as e:
            logger.exception("Image URL fetch failed")
            raise HTTPException(status_code=400, detail=f"Image URL fetch failed: {e}")
    elif image:
        image_bytes = await image.read()

    if image_bytes:
        encoded = base64.b64encode(image_bytes).decode()
        image_url_final = upload_to_imgbb_with_retry(encoded)

    # 5) Upsert locally
    try:
        await upsert_product_local(
            shopify_gid=product_gid,
            product_data={
                "name": name,
                "description": description,
                "price": price,
                "image": image_url_final,
                "variants": [{"shopify_id": variant_gid, "title": "Default", "price": price}],
            },
        )
    except Exception:
        logger.exception("Non-fatal: failed to upsert locally")

    # 6) Optionally add to local cart (session)
    session_id = request.headers.get("x-session-id")
    cart_data = None
    if session_id:
        cart_service = get_cart_service()
        for attempt in range(1, 3):
            try:
                cart = await cart_service.add_item_to_cart(session_id, product_gid, variant_gid, quantity)
            except Exception as e:
                logger.error("Error adding to local cart: %s", e)
                cart = None
            if cart:
                cart_data = cart
                break
            await asyncio.sleep(2)

    # 7) Ensure storefront sees the variant before calling cartCreate
    visible = wait_for_variant_in_storefront(variant_gid, timeout=1000, interval=2)
    if not visible:
        # Try a second publish or longer wait before failing (optional)
        logger.warning("Variant not visible in Storefront after initial wait; sleeping extra 5s and retrying check.")
        time.sleep(5)
        visible = wait_for_variant_in_storefront(variant_gid, timeout=20, interval=2)
    if not visible:
        raise HTTPException(status_code=500, detail="Variant not visible in Storefront; cannot create checkout yet.")

    # 8) Create checkout via cartCreate
    checkout_url = None
    try:
        checkout_url = create_shopify_checkout(variant_gid, int(quantity), max_retries=3)
    except HTTPException as e:
        logger.error("Failed to create checkout: %s", e.detail)
        raise

    # 9) Return result
    return {
        "message": "✅ Product created, published, and checkout ready",
        "product_id": product_gid,
        "variant_id": variant_gid,
        "price": price,
        "checkout_url": checkout_url,
        "image_url": image_url_final,
        "admin_url": f"https://{SHOPIFY_STORE}/admin/products/{numeric_id}",
        "cart": cart_data,
    }
