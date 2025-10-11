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


class Design(BaseModel):
    id: str
    name: str
    src: str
    width: float
    height: float
    original_width: int
    original_height: int
    x: float
    y: float
    rotation: float = 0.0
    quantity: int = 1

    class Config:
        schema_extra = {
            "example": {
                "id": "design_123",
                "name": "logo.png",
                "src": "data:image/png;base64,iVBOR...",
                "width": 100.0,
                "height": 100.0,
                "original_width": 300,
                "original_height": 300,
                "x": 50.0,
                "y": 50.0,
                "rotation": 0.0,
                "quantity": 1
            }
        }


class GangSheetTemplate(BaseModel):
    id: str
    name: str
    width: float
    height: float
    price: float
    max_designs: int


class GangSheetBase(BaseModel):
    template_id: str
    template_name: str
    width: float
    height: float
    base_price: float
    designs: List[Design] = []
    status: str = "draft"

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class GangSheetCreate(GangSheetBase):
    user_id: Optional[str] = None


class GangSheetUpdate(BaseModel):
    designs: Optional[List[Design]] = None
    status: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class GangSheet(GangSheetBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: Optional[str] = None
    total_price: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

    def calculate_total_price(self):
        """Calculate total price based on base price + design count"""
        design_count = sum(design.quantity for design in self.designs)
        self.total_price = self.base_price + (design_count * 0.50)
        return self.total_price


class DesignUpload(BaseModel):
    name: str
    file_data: str  # Base64 encoded image data
    x: Optional[float] = 50.0
    y: Optional[float] = 50.0
    quantity: Optional[int] = 1