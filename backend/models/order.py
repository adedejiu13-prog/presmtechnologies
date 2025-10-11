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


class OrderItem(BaseModel):
    product_id: Optional[str] = None
    gang_sheet_id: Optional[str] = None
    name: str
    quantity: int
    price: float
    options: Dict[str, Any] = {}

    class Config:
        schema_extra = {
            "example": {
                "product_id": "60f7b3b3b3b3b3b3b3b3b3b3",
                "name": "Standard DTF Transfer",
                "quantity": 2,
                "price": 2.50,
                "options": {"size": "4x4"}
            }
        }


class ShippingAddress(BaseModel):
    first_name: str
    last_name: str
    address1: str
    address2: Optional[str] = None
    city: str
    province: str
    zip_code: str
    country: str
    phone: Optional[str] = None


class OrderBase(BaseModel):
    customer_id: Optional[str] = None
    items: List[OrderItem]
    subtotal: float
    shipping: float = 0.0
    tax: float = 0.0
    total: float
    status: str = "pending"
    shipping_address: Optional[ShippingAddress] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    shopify_order_id: Optional[str] = None
    tracking_number: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class Order(OrderBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    shopify_order_id: Optional[str] = None
    tracking_number: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}