from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from models.cart import Cart, CartItem, CartItemCreate, CartItemUpdate
from models.product import Product
from models.gang_sheet import GangSheet
from services.database import get_carts_collection


class CartService:
    def __init__(self):
        self.collection = None
    
    def _get_collection(self):
        if self.collection is None:
            self.collection = get_carts_collection()
        return self.collection

    async def get_or_create_cart(self, session_id: str, user_id: Optional[str] = None) -> Cart:
        """Get existing cart or create new one"""
        collection = self._get_collection()
        cart = await collection.find_one({"session_id": session_id})
        
        if cart:
            return Cart(**cart)
        
        # Create new cart
        new_cart = Cart(
            session_id=session_id,
            user_id=user_id,
            items=[]
        )
        
        result = await collection.insert_one(new_cart.dict())
        created_cart = await collection.find_one({"_id": result.inserted_id})
        return Cart(**created_cart)

    async def add_item_to_cart(self, session_id: str, item_data: CartItemCreate) -> Optional[Cart]:
        """Add item to cart"""
        cart = await self.get_or_create_cart(session_id)
        
        # Get product or gang sheet details
        cart_item = None
        
        if item_data.product_id:
            from utils import get_product_service
            product = await get_product_service().get_product_by_id(item_data.product_id)
            if not product:
                return None
                
            cart_item = CartItem(
                product_id=item_data.product_id,
                name=product.name,
                price=product.price,
                image=product.image,
                description=product.description,
                quantity=item_data.quantity,
                options=item_data.options
            )
        
        elif item_data.gang_sheet_id:
            from utils import get_gang_sheet_service
            gang_sheet = await get_gang_sheet_service().get_gang_sheet_by_id(item_data.gang_sheet_id)
            if not gang_sheet:
                return None
                
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
        
        if not cart_item:
            return None

        # Check if item already exists in cart (same product/gang_sheet + options)
        existing_item = None
        for item in cart.items:
            if ((item.product_id == cart_item.product_id and item.product_id) or
                (item.gang_sheet_id == cart_item.gang_sheet_id and item.gang_sheet_id)) and \
               item.options == cart_item.options:
                existing_item = item
                break

        if existing_item:
            existing_item.quantity += cart_item.quantity
        else:
            cart.items.append(cart_item)

        cart.updated_at = datetime.utcnow()

        # Update in database
        collection = self._get_collection()
        await collection.update_one(
            {"_id": cart.id},
            {
                "$set": {
                    "items": [item.dict() for item in cart.items],
                    "updated_at": cart.updated_at
                }
            }
        )

        return cart

    async def update_cart_item(self, session_id: str, item_index: int, update_data: CartItemUpdate) -> Optional[Cart]:
        """Update cart item quantity"""
        cart = await self.get_or_create_cart(session_id)
        
        if item_index < 0 or item_index >= len(cart.items):
            return None

        if update_data.quantity <= 0:
            # Remove item if quantity is 0 or negative
            cart.items.pop(item_index)
        else:
            cart.items[item_index].quantity = update_data.quantity

        cart.updated_at = datetime.utcnow()

        # Update in database
        collection = self._get_collection()
        await collection.update_one(
            {"_id": cart.id},
            {
                "$set": {
                    "items": [item.dict() for item in cart.items],
                    "updated_at": cart.updated_at
                }
            }
        )

        return cart

    async def remove_cart_item(self, session_id: str, item_index: int) -> Optional[Cart]:
        """Remove item from cart"""
        cart = await self.get_or_create_cart(session_id)
        
        if item_index < 0 or item_index >= len(cart.items):
            return None

        cart.items.pop(item_index)
        cart.updated_at = datetime.utcnow()

        # Update in database
        collection = self._get_collection()
        await collection.update_one(
            {"_id": cart.id},
            {
                "$set": {
                    "items": [item.dict() for item in cart.items],
                    "updated_at": cart.updated_at
                }
            }
        )

        return cart

    async def clear_cart(self, session_id: str) -> Optional[Cart]:
        """Clear all items from cart"""
        cart = await self.get_or_create_cart(session_id)
        cart.items = []
        cart.updated_at = datetime.utcnow()

        # Update in database
        collection = self._get_collection()
        await collection.update_one(
            {"_id": cart.id},
            {
                "$set": {
                    "items": [],
                    "updated_at": cart.updated_at
                }
            }
        )

        return cart

    async def get_cart(self, session_id: str) -> Cart:
        """Get cart with calculated totals"""
        return await self.get_or_create_cart(session_id)


# Global service instance - will be initialized after database connection
cart_service = None

def get_cart_service():
    global cart_service
    if cart_service is None:
        cart_service = CartService()
    return cart_service