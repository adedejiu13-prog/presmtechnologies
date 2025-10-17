from services.product_service import ProductService
from services.cart_service import CartService

def get_product_service():
    return ProductService()

def get_cart_service():
    return CartService()