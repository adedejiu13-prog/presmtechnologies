"""Utility functions for lazy service initialization"""

from services.product_service import ProductService
from services.gang_sheet_service import GangSheetService
from services.cart_service import CartService

_product_service = None
_gang_sheet_service = None
_cart_service = None

def get_product_service():
    global _product_service
    if _product_service is None:
        _product_service = ProductService()
    return _product_service

def get_gang_sheet_service():
    global _gang_sheet_service
    if _gang_sheet_service is None:
        _gang_sheet_service = GangSheetService()
    return _gang_sheet_service

def get_cart_service():
    global _cart_service
    if _cart_service is None:
        _cart_service = CartService()
    return _cart_service