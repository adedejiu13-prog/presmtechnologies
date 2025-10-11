from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from models.product import Product, ProductCreate, ProductUpdate
from services.database import get_products_collection


class ProductService:
    def __init__(self):
        self.collection = None
    
    def _get_collection(self):
        if self.collection is None:
            self.collection = get_products_collection()
        return self.collection

    async def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        collection = self._get_collection()
        product_dict = product_data.dict()
        result = await collection.insert_one(product_dict)
        created_product = await collection.find_one({"_id": result.inserted_id})
        return Product(**created_product)

    async def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get product by ID"""
        if not ObjectId.is_valid(product_id):
            return None
        
        collection = self._get_collection()
        product = await collection.find_one({"_id": ObjectId(product_id)})
        if product:
            return Product(**product)
        return None

    async def get_products(self, 
                          category: Optional[str] = None, 
                          status: str = "active",
                          skip: int = 0, 
                          limit: int = 100) -> List[Product]:
        """Get products with optional filtering"""
        collection = self._get_collection()
        query = {"status": status}
        if category:
            query["category"] = category

        cursor = collection.find(query).skip(skip).limit(limit)
        products = []
        async for product in cursor:
            products.append(Product(**product))
        return products

    async def update_product(self, product_id: str, product_data: ProductUpdate) -> Optional[Product]:
        """Update product"""
        if not ObjectId.is_valid(product_id):
            return None

        collection = self._get_collection()
        update_data = {k: v for k, v in product_data.dict().items() if v is not None}
        if not update_data:
            return await self.get_product_by_id(product_id)

        update_data["updated_at"] = datetime.utcnow()
        
        result = await collection.update_one(
            {"_id": ObjectId(product_id)}, 
            {"$set": update_data}
        )
        
        if result.modified_count:
            return await self.get_product_by_id(product_id)
        return None

    async def delete_product(self, product_id: str) -> bool:
        """Delete product (soft delete by setting status to archived)"""
        if not ObjectId.is_valid(product_id):
            return False

        collection = self._get_collection()
        result = await collection.update_one(
            {"_id": ObjectId(product_id)}, 
            {"$set": {"status": "archived", "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def search_products(self, query: str, category: Optional[str] = None) -> List[Product]:
        """Search products by name or description"""
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
            products.append(Product(**product))
        return products

    async def get_categories(self) -> List[dict]:
        """Get all product categories with counts"""
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
        return categories


# Global service instance - will be initialized after database connection
product_service = None

def get_product_service():
    global product_service
    if product_service is None:
        product_service = ProductService()
    return product_service