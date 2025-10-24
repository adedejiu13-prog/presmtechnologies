import logging
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from services.database import SessionLocal
from models.cart import Cart
from models.product import Product
import json

logger = logging.getLogger("cart_service")
logging.basicConfig(level=logging.INFO)


class CartService:
    async def get_or_create_cart(self, session_id: str) -> Cart:
        """Retrieve an existing cart or create a new one."""
        async with SessionLocal() as session:
            try:
                result = await session.execute(
                    select(Cart).where(Cart.session_id == session_id)
                )
                cart = result.scalars().first()

                if cart:
                    logger.info(f"🛒 Found existing cart for {session_id}")
                    return cart

                new_cart = Cart(
                    session_id=session_id,
                    items=[],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(new_cart)
                await session.commit()
                await session.refresh(new_cart)
                logger.info(f"🆕 Created new cart for session: {session_id}")
                return new_cart

            except SQLAlchemyError as e:
                logger.error(f"❌ Database error creating cart: {e}")
                return None

    async def add_item_to_cart(
        self,
        session_id: str,
        product_id: str,
        variant_id: str,
        quantity: int = 1,
    ):
        """Add an item to a user's cart."""
        async with SessionLocal() as session:
            try:
                # Get or create cart
                result = await session.execute(
                    select(Cart).where(Cart.session_id == session_id)
                )
                cart = result.scalars().first()

                if not cart:
                    cart = Cart(
                        session_id=session_id,
                        items=[],
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    session.add(cart)
                    await session.commit()
                    await session.refresh(cart)
                    logger.info(f"🆕 Created new cart for session: {session_id}")

                # Fetch product
                result = await session.execute(
                    select(Product).where(Product.shopify_id == product_id)
                )
                product = result.scalars().first()
                if not product:
                    logger.error(f"❌ Product {product_id} not found in DB")
                    return None

                # Ensure variants exist
                variants = product.variants or []
                # Handle GID normalization
                variant = next(
                    (
                        v for v in variants
                        if str(v.get("shopify_id")).split("/")[-1] == str(variant_id).split("/")[-1]
                    ),
                    None,
                )
                if not variant:
                    logger.error(f"❌ Variant {variant_id} not found for product {product_id}")
                    return None

                # Convert cart.items from string to list if necessary
                if isinstance(cart.items, str):
                    try:
                        cart.items = json.loads(cart.items)
                    except Exception:
                        cart.items = []

                items = list(cart.items or [])
                existing = next((i for i in items if str(i["variant_id"]) == str(variant_id)), None)

                if existing:
                    existing["quantity"] += quantity
                else:
                    items.append({
                        "product_id": product_id,
                        "variant_id": variant_id,
                        "name": f"{product.name} - {variant.get('title', 'Default')}",
                        "price": float(variant.get("price", 0)),
                        "quantity": quantity,
                    })

                cart.items = items
                cart.updated_at = datetime.utcnow()
                session.add(cart)
                await session.commit()
                await session.refresh(cart)
                logger.info(f"✅ Added variant {variant_id} to cart for session {session_id}")

                # Return cart as dict (JSON serializable)
                return {
                    "id": cart.id,
                    "session_id": cart.session_id,
                    "items": cart.items,
                    "created_at": cart.created_at.isoformat(),
                    "updated_at": cart.updated_at.isoformat(),
                }

            except SQLAlchemyError as e:
                logger.error(f"❌ Error updating cart: {e}")
                await session.rollback()
                return None


cart_service = CartService()


def get_cart_service():
    return cart_service
