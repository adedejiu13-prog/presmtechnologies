import logging
from datetime import datetime
from sqlalchemy import select
from services.database import SessionLocal
from models.cart import Cart
from models.product import Product

logger = logging.getLogger("cart_service")
logging.basicConfig(level=logging.INFO)


class CartService:
    async def get_or_create_cart(self, session_id: str) -> Cart:
        """Get existing cart or create a new one."""
        async with SessionLocal() as session:
            result = await session.execute(
                select(Cart).where(Cart.session_id == session_id)
            )
            cart = result.scalars().first()
            if cart:
                return cart

            new_cart = Cart(
                session_id=session_id,
                items=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(new_cart)
            await session.flush()
            await session.commit()
            logger.info(f"Created new cart for session: {session_id}")
            return new_cart

    async def add_item_to_cart(
        self,
        session_id: str,
        product_id: str,
        variant_id: str,
        quantity: int = 1
    ):
        """Add an item to cart, creating the cart if necessary."""
        async with SessionLocal() as session:
            cart = await self.get_or_create_cart(session_id)

            # Fetch product from DB
            result = await session.execute(
                select(Product).where(Product.shopify_id == product_id)
            )
            product = result.scalars().first()
            if not product:
                logger.error(f"Product {product_id} not found in DB")
                return None

            # Find the variant
            variant = next((v for v in product.variants if str(v["shopify_id"]) == str(variant_id)), None)
            if not variant:
                logger.error(f"Variant {variant_id} not found for product {product_id}")
                return None

            # Check if item already exists in cart
            existing_item = next((i for i in cart.items if str(i["variant_id"]) == str(variant_id)), None)
            if existing_item:
                existing_item["quantity"] += quantity
            else:
                cart.items.append({
                    "product_id": product_id,
                    "variant_id": variant_id,
                    "name": f"{product.name} - {variant['title']}",
                    "price": variant["price"],
                    "quantity": quantity
                })

            cart.updated_at = datetime.utcnow()
            session.add(cart)
            await session.flush()
            await session.commit()
            logger.info(f"Added variant {variant_id} to cart {session_id}")
            return cart


cart_service = CartService()


def get_cart_service():
    return cart_service
