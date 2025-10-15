from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from models.product import Product, ProductCreate, ProductUpdate
from services.database import get_products_collection
import logging

logger = logging.getLogger("product_service")
logging.basicConfig(level=logging.INFO)

class ProductService:
    def __init__(self):
        self.collection = None
    
    def _get_collection(self):
        if self.collection is None:
            self.collection = get_products_collection()
        return self.collection

    async def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        try:
            collection = self._get_collection()
            product_dict = product_data.model_dump(by_alias=True)
            result = await collection.insert_one(product_dict)
            created_product = await collection.find_one({"_id": result.inserted_id})
            logger.info(f"Product created: {created_product['_id']}")
            return Product.model_validate(created_product)
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            raise

    async def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID (MongoDB ObjectId or Shopify GID)"""
        try:
            collection = self._get_collection()
            if ObjectId.is_valid(product_id):
                product = await collection.find_one({"_id": ObjectId(product_id)})
            else:
                product = await collection.find_one({"shopify_id": product_id})
            if product:
                logger.info(f"Product found: {product_id}")
                return Product.model_validate(product)
            logger.warning(f"Product not found: {product_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {e}")
            return None

    async def get_products(self, 
                          category: Optional[str] = None, 
                          status: str = "active",
                          skip: int = 0, 
                          limit: int = 100) -> List[Product]:
        """Get products with optional filtering"""
        try:
            collection = self._get_collection()
            query = {"status": status}
            if category:
                query["category"] = category

            cursor = collection.find(query).skip(skip).limit(limit)
            products = []
            async for product in cursor:
                products.append(Product.model_validate(product))
            logger.info(f"Fetched {len(products)} products")
            return products
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            return []

    async def update_product(self, product_id: str, product_data: ProductUpdate) -> Optional[Product]:
        """Update product"""
        try:
            if not ObjectId.is_valid(product_id):
                logger.warning(f"Invalid ObjectId: {product_id}")
                return None

            collection = self._get_collection()
            update_data = {k: v for k, v in product_data.model_dump(by_alias=True).items() if v is not None}
            if not update_data:
                return await self.get_product(product_id)

            update_data["updated_at"] = datetime.utcnow()
            
            result = await collection.update_one(
                {"_id": ObjectId(product_id)}, 
                {"$set": update_data}
            )
            
            if result.modified_count:
                logger.info(f"Product updated: {product_id}")
                return await self.get_product(product_id)
            logger.warning(f"No changes made to product: {product_id}")
            return None
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {e}")
            return None

    async def delete_product(self, product_id: str) -> bool:
        """Delete product (soft delete by setting status to archived)"""
        try:
            if not ObjectId.is_valid(product_id):
                logger.warning(f"Invalid ObjectId: {product_id}")
                return False

            collection = self._get_collection()
            result = await collection.update_one(
                {"_id": ObjectId(product_id)}, 
                {"$set": {"status": "archived", "updated_at": datetime.utcnow()}}
            )
            if result.modified_count:
                logger.info(f"Product archived: {product_id}")
                return True
            logger.warning(f"Product not found for deletion: {product_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}")
            return False

    async def search_products(self, query: str, category: Optional[str] = None) -> List[Product]:
        """Search products by name or description"""
        try:
            collection = self._get_collection()
            search_query = {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}}
                ],
                "status": "active"
            }
            if category:
                search_query["category"] = category

            cursor = collection.find(search_query)
            products = []
            async for product in cursor:
                products.append(Product.model_validate(product))
            logger.info(f"Found {len(products)} products for query: {query}")
            return products
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []

    async def get_categories(self) -> List[dict]:
        """Get all product categories with counts"""
        try:
            collection = self._get_collection()
            pipeline = [
                {"$match": {"status": "active"}},
                {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                {"$project": {"category": "$_id", "count": 1, "_id": 0}},
                {"$sort": {"category": 1}}
            ]
            
            categories = []
            async for category in collection.aggregate(pipeline):
                categories.append(category)
            logger.info(f"Fetched {len(categories)} categories")
            return categories
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return []

# Global service instance
product_service = None

def get_product_service():
    global product_service
    if product_service is None:
        product_service = ProductService()
    return product_service