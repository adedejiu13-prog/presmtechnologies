from typing import Dict, Optional
from datetime import datetime
from models.cart import Cart, CartItem, CartItemCreate, CartItemUpdate


class InMemoryCartService:
    """In-memory cart service for development without database"""
    
    def __init__(self):
        self.carts: Dict[str, Cart] = {}
    
    async def get_or_create_cart(self, session_id: str, user_id: Optional[str] = None) -> Cart:
        """Get existing cart or create new one"""
        if session_id not in self.carts:
            self.carts[session_id] = Cart(
                session_id=session_id,
                user_id=user_id,
                items=[]
            )
        return self.carts[session_id]
    
    async def add_item_to_cart(self, session_id: str, item_data: CartItemCreate) -> Optional[Cart]:
        """Add item to cart"""
        cart = await self.get_or_create_cart(session_id)
        
        # Create cart item from provided data
        cart_item = CartItem(
            product_id=item_data.product_id,
            variant_id=getattr(item_data, 'variant_id', None),
            name=item_data.name,
            price=item_data.price,
            image=getattr(item_data, 'image', ''),
            description=getattr(item_data, 'description', ''),
            quantity=item_data.quantity,
            options=item_data.options if hasattr(item_data, 'options') else {}
        )
        
        # Check if item already exists
        existing_item = None
        for item in cart.items:
            if item.product_id == cart_item.product_id and item.variant_id == cart_item.variant_id:
                existing_item = item
                break
        
        if existing_item:
            existing_item.quantity += cart_item.quantity
        else:
            cart.items.append(cart_item)
        
        cart.updated_at = datetime.utcnow()
        return cart
    
    async def update_cart_item(self, session_id: str, item_index: int, update_data: CartItemUpdate) -> Optional[Cart]:
        """Update cart item quantity"""
        cart = await self.get_or_create_cart(session_id)
        
        if item_index < 0 or item_index >= len(cart.items):
            return None
        
        if update_data.quantity <= 0:
            cart.items.pop(item_index)
        else:
            cart.items[item_index].quantity = update_data.quantity
        
        cart.updated_at = datetime.utcnow()
        return cart
    
    async def remove_cart_item(self, session_id: str, item_index: int) -> Optional[Cart]:
        """Remove item from cart"""
        cart = await self.get_or_create_cart(session_id)
        
        if item_index < 0 or item_index >= len(cart.items):
            return None
        
        cart.items.pop(item_index)
        cart.updated_at = datetime.utcnow()
        return cart
    
    async def clear_cart(self, session_id: str) -> Cart:
        """Clear all items from cart"""
        cart = await self.get_or_create_cart(session_id)
        cart.items = []
        cart.updated_at = datetime.utcnow()
        return cart
    
    async def get_cart(self, session_id: str) -> Cart:
        """Get cart"""
        return await self.get_or_create_cart(session_id)
