from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from models.product import Product, ProductCreate, ProductUpdate
from services.database import get_products_collection
import logging

logger = logging.getLogger("product_service")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

class ProductService:
    def __init__(self):
        self.collection = None
    
    def _get_collection(self):
        if self.collection is None:
            self.collection = get_products_collection()
            if self.collection is None:
                logger.error("Products collection not initialized")
                raise RuntimeError("Products collection not initialized")
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
                logger.debug(f"Product found: {product_id}")
                return Product.model_validate(product)
            logger.warning(f"Product not found: {product_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {e}")
            raise

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

def get_product_service():
    return ProductService()