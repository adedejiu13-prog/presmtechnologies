from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
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


class CartItem(BaseModel):
    product_id: Optional[str] = None
    gang_sheet_id: Optional[str] = None
    name: str
    price: float
    image: str
    description: str
    quantity: int
    options: Dict[str, Any] = {}

    class Config:
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "product_id": "60f7b3b3b3b3b3b3b3b3b3b3",
                "name": "Standard DTF Transfer",
                "price": 2.50,
                "image": "https://example.com/image.jpg",
                "description": "High-quality DTF transfer",
                "quantity": 2,
                "options": {"size": "4x4"}
            }
        }


class CartItemCreate(BaseModel):
    product_id: Optional[str] = None
    gang_sheet_id: Optional[str] = None
    quantity: int = 1
    options: Dict[str, Any] = {}


class CartItemUpdate(BaseModel):
    quantity: int

    class Config:
        schema_extra = {
            "example": {
                "quantity": 3
            }
        }


class Cart(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    session_id: str
    user_id: Optional[str] = None
    items: List[CartItem] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

    def get_total_items(self) -> int:
        return sum(item.quantity for item in self.items)

    def get_total_price(self) -> float:
        return sum(item.price * item.quantity for item in self.items)

    def get_subtotal(self) -> float:
        return self.get_total_price()

    def get_shipping_cost(self) -> float:
        return 0.0 if self.get_subtotal() >= 75.0 else 9.99

    def get_tax(self) -> float:
        return self.get_subtotal() * 0.08  # 8% tax

    def get_order_total(self) -> float:
        return self.get_subtotal() + self.get_shipping_cost() + self.get_tax()