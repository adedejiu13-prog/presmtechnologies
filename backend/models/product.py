from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

class Variant(BaseModel):
    shopify_id: str
    title: str
    price: float
    available: bool = True

class ProductBase(BaseModel):
    name: str
    category: str
    price: float
    image: str
    images: List[str] = []
    description: str
    features: List[str] = []
    sizes: List[str] = []
    min_quantity: int = 1
    max_quantity: int = 1000
    inventory: int = 100
    status: str = "active"
    variants: List[Variant] = []

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    images: Optional[List[str]] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    sizes: Optional[List[str]] = None
    min_quantity: Optional[int] = None
    max_quantity: Optional[int] = None
    inventory: Optional[int] = None
    status: Optional[str] = None
    variants: Optional[List[Variant]] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class Product(ProductBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    shopify_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Standard DTF Transfer",
                "category": "dtf-transfers",
                "price": 2.50,
                "image": "https://example.com/image.jpg",
                "images": ["https://example.com/image.jpg"],
                "description": "High-quality direct-to-film transfers",
                "features": ["Premium PET film", "Vivid colors", "Cold peel"],
                "sizes": ["2x2", "3x3", "4x4"],
                "min_quantity": 1,
                "max_quantity": 1000,
                "inventory": 100,
                "status": "active",
                "variants": [
                    {
                        "shopify_id": "gid://shopify/ProductVariant/456",
                        "title": "Default Variant",
                        "price": 2.50,
                        "available": True
                    }
                ]
            }
        }