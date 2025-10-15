from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from models.cart import Cart, CartItem, CartItemCreate, CartItemUpdate
from models.product import Product
from models.gang_sheet import GangSheet
from services.database import get_carts_collection
import logging

logger = logging.getLogger("cart_service")
logging.basicConfig(level=logging.INFO)

class CartService:
    def __init__(self):
        self.collection = None

    def _get_collection(self):
        if self.collection is None:
            self.collection = get_carts_collection()
        return self.collection

    async def get_or_create_cart(self, session_id: str, user_id: Optional[str] = None) -> Cart:
        """Get existing cart or create new one"""
        try:
            collection = self._get_collection()
            cart_doc = await collection.find_one({"session_id": session_id})

            if cart_doc:
                logger.info(f"Found existing cart for session: {session_id}")
                return Cart.model_validate(cart_doc)

            # Create new cart
            new_cart = Cart(session_id=session_id, user_id=user_id, items=[])
            result = await collection.insert_one(new_cart.model_dump(by_alias=True))
            created_cart = await collection.find_one({"_id": result.inserted_id})
            logger.info(f"Created new cart for session: {session_id}")
            return Cart.model_validate(created_cart)
        except Exception as e:
            logger.error(f"Error getting or creating cart for session {session_id}: {e}")
            raise

    async def add_item_to_cart(self, session_id: str, item_data: CartItemCreate) -> Optional[Cart]:
        """Add a product or gang sheet to the cart"""
        try:
            cart = await self.get_or_create_cart(session_id)
            cart_item = None

            if item_data.product_id:
                from utils import get_product_service
                product = await get_product_service().get_product(item_data.product_id)
                if not product:
                    logger.error(f"Product not found in MongoDB: {item_data.product_id}")
                    raise ValueError(f"Product not found: {item_data.product_id}")

                variant_id = item_data.variant_id
                if not variant_id:
                    logger.error(f"Variant ID required for product: {item_data.product_id}")
                    raise ValueError("Variant ID required")

                variant = next((v for v in product.variants if v.shopify_id == variant_id), None)
                if not variant:
                    logger.error(f"Variant not found: {variant_id} for product: {item_data.product_id}")
                    raise ValueError(f"Variant not found: {variant_id}")

                cart_item = CartItem(
                    product_id=item_data.product_id,
                    variant_id=variant_id,
                    name=f"{product.name} - {variant.title}",
                    price=variant.price,
                    image=product.image,
                    description=product.description,
                    quantity=item_data.quantity,
                    options=item_data.options or {}
                )
                logger.info(f"Created cart item for product: {item_data.product_id}, variant: {variant_id}")

            elif item_data.gang_sheet_id:
                from utils import get_gang_sheet_service
                gang_sheet = await get_gang_sheet_service().get_gang_sheet_by_id(item_data.gang_sheet_id)
                if not gang_sheet:
                    logger.error(f"Gang sheet not found: {item_data.gang_sheet_id}")
                    raise ValueError(f"Gang sheet not found: {item_data.gang_sheet_id}")

                cart_item = CartItem(
                    gang_sheet_id=item_data.gang_sheet_id,
                    name=f"Custom Gang Sheet ({gang_sheet.template_name})",
                    price=gang_sheet.total_price,
                    image="https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=400&fit=crop",
                    description=f"Custom gang sheet with {len(gang_sheet.designs)} designs",
                    quantity=item_data.quantity,
                    options={
                        "template": gang_sheet.template_name,
                        "designs": len(gang_sheet.designs),
                        "total_quantity": sum(d.quantity for d in gang_sheet.designs)
                    }
                )
                logger.info(f"Created cart item for gang sheet: {item_data.gang_sheet_id}")

            if not cart_item:
                logger.error("No valid cart item created")
                raise ValueError("No valid cart item created")

            # Merge if the item already exists in cart
            existing_item = next(
                (i for i in cart.items if (
                    (i.product_id == cart_item.product_id and i.product_id and i.variant_id == cart_item.variant_id) or
                    (i.gang_sheet_id == cart_item.gang_sheet_id and i.gang_sheet_id)
                ) and i.options == cart_item.options),
                None
            )

            if existing_item:
                existing_item.quantity += cart_item.quantity
                logger.info(f"Merged item with existing cart item for session: {session_id}")
            else:
                cart.items.append(cart_item)
                logger.info(f"Appended new item to cart for session: {session_id}")

            cart.updated_at = datetime.utcnow()

            collection = self._get_collection()
            logger.info(f"Updating cart with items: {[item.model_dump(by_alias=True) for item in cart.items]}")
            await collection.update_one(
                {"_id": cart.id},
                {"$set": {
                    "items": [item.model_dump(by_alias=True) for item in cart.items],
                    "updated_at": cart.updated_at
                }}
            )
            logger.info(f"Cart updated in database for session: {session_id}")
            return cart

        except ValueError as e:
            logger.error(f"ValueError adding item to cart for session {session_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error adding item to cart for session {session_id}: {str(e)}")
            raise

    async def update_cart_item(self, session_id: str, item_index: int, update_data: CartItemUpdate) -> Optional[Cart]:
        """Update cart item quantity"""
        try:
            cart = await self.get_or_create_cart(session_id)
            if item_index < 0 or item_index >= len(cart.items):
                logger.error(f"Invalid item index: {item_index} for session {session_id}")
                raise ValueError(f"Invalid item index: {item_index}")

            if update_data.quantity <= 0:
                cart.items.pop(item_index)
                logger.info(f"Removed item at index {item_index} due to zero quantity for session: {session_id}")
            else:
                cart.items[item_index].quantity = update_data.quantity
                logger.info(f"Updated item quantity at index {item_index} for session: {session_id}")

            cart.updated_at = datetime.utcnow()
            collection = self._get_collection()
            await collection.update_one(
                {"_id": cart.id},
                {"$set": {
                    "items": [item.model_dump(by_alias=True) for item in cart.items],
                    "updated_at": cart.updated_at
                }}
            )
            logger.info(f"Cart updated for session: {session_id}")
            return cart
        except ValueError as e:
            logger.error(f"ValueError updating cart item at index {item_index} for session {session_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating cart item at index {item_index} for session {session_id}: {str(e)}")
            raise

    async def remove_cart_item(self, session_id: str, item_index: int) -> Optional[Cart]:
        """Remove item from cart"""
        try:
            cart = await self.get_or_create_cart(session_id)
            if item_index < 0 or item_index >= len(cart.items):
                logger.error(f"Invalid item index: {item_index} for session {session_id}")
                raise ValueError(f"Invalid item index: {item_index}")

            cart.items.pop(item_index)
            cart.updated_at = datetime.utcnow()
            collection = self._get_collection()
            await collection.update_one(
                {"_id": cart.id},
                {"$set": {
                    "items": [item.model_dump(by_alias=True) for item in cart.items],
                    "updated_at": cart.updated_at
                }}
            )
            logger.info(f"Cart item removed at index {item_index} for session: {session_id}")
            return cart
        except ValueError as e:
            logger.error(f"ValueError removing cart item at index {item_index} for session {session_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error removing cart item at index {item_index} for session {session_id}: {str(e)}")
            raise

    async def clear_cart(self, session_id: str) -> Optional[Cart]:
        """Clear all items from cart"""
        try:
            cart = await self.get_or_create_cart(session_id)
            cart.items = []
            cart.updated_at = datetime.utcnow()
            collection = self._get_collection()
            await collection.update_one(
                {"_id": cart.id},
                {"$set": {
                    "items": [],
                    "updated_at": cart.updated_at
                }}
            )
            logger.info(f"Cart cleared for session: {session_id}")
            return cart
        except Exception as e:
            logger.error(f"Error clearing cart for session {session_id}: {e}")
            raise

    async def get_cart(self, session_id: str) -> Cart:
        """Get cart"""
        try:
            cart = await self.get_or_create_cart(session_id)
            logger.info(f"Cart retrieved for session: {session_id}")
            return cart
        except Exception as e:
            logger.error(f"Error retrieving cart for session {session_id}: {e}")
            raise

# Global instance
cart_service = CartService()

def get_cart_service():
    global cart_service
    if cart_service is None:
        cart_service = CartService()
    return cart_service