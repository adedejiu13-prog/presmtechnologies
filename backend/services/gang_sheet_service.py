from typing import List, Optional
from bson import ObjectId
from datetime import datetime
import base64
import io
from PIL import Image
from models.gang_sheet import GangSheet, GangSheetCreate, GangSheetUpdate, Design, DesignUpload
from services.database import get_gang_sheets_collection
import random
import math


class GangSheetService:
    def __init__(self):
        self.collection = None
    
    def _get_collection(self):
        if self.collection is None:
            self.collection = get_gang_sheets_collection()
        return self.collection

    async def create_gang_sheet(self, gang_sheet_data: GangSheetCreate) -> GangSheet:
        """Create a new gang sheet"""
        gang_sheet_dict = gang_sheet_data.dict()
        gang_sheet_dict["created_at"] = datetime.utcnow()
        gang_sheet_dict["updated_at"] = datetime.utcnow()
        
        collection = self._get_collection()
        result = await collection.insert_one(gang_sheet_dict)
        created_gang_sheet = await self.collection.find_one({"_id": result.inserted_id})
        return GangSheet(**created_gang_sheet)

    async def get_gang_sheet_by_id(self, gang_sheet_id: str) -> Optional[GangSheet]:
        """Get gang sheet by ID"""
        if not ObjectId.is_valid(gang_sheet_id):
            return None
        
        gang_sheet = await self.collection.find_one({"_id": ObjectId(gang_sheet_id)})
        if gang_sheet:
            return GangSheet(**gang_sheet)
        return None

    async def get_gang_sheets_by_user(self, user_id: str, skip: int = 0, limit: int = 50) -> List[GangSheet]:
        """Get gang sheets for a user"""
        cursor = self.collection.find({"user_id": user_id}).skip(skip).limit(limit).sort("created_at", -1)
        gang_sheets = []
        async for sheet in cursor:
            gang_sheets.append(GangSheet(**sheet))
        return gang_sheets

    async def add_design_to_sheet(self, gang_sheet_id: str, design: DesignUpload) -> Optional[GangSheet]:
        """Add a design to gang sheet"""
        if not ObjectId.is_valid(gang_sheet_id):
            return None

        gang_sheet = await self.get_gang_sheet_by_id(gang_sheet_id)
        if not gang_sheet:
            return None

        # Process the uploaded image
        try:
            # Decode base64 image
            image_data = design.file_data
            if "," in image_data:
                image_data = image_data.split(",")[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Create design object
            design_obj = Design(
                id=f"design_{int(datetime.utcnow().timestamp() * 1000)}",
                name=design.name,
                src=design.file_data,
                width=min(image.width / 10, 100),  # Scale down for canvas
                height=min(image.height / 10, 100),
                original_width=image.width,
                original_height=image.height,
                x=design.x or 50.0,
                y=design.y or 50.0,
                rotation=0.0,
                quantity=design.quantity or 1
            )

            # Add design to gang sheet
            gang_sheet.designs.append(design_obj)
            gang_sheet.calculate_total_price()
            gang_sheet.updated_at = datetime.utcnow()

            # Update in database
            await self.collection.update_one(
                {"_id": ObjectId(gang_sheet_id)},
                {
                    "$set": {
                        "designs": [design.dict() for design in gang_sheet.designs],
                        "total_price": gang_sheet.total_price,
                        "updated_at": gang_sheet.updated_at
                    }
                }
            )

            return gang_sheet

        except Exception as e:
            print(f"Error processing design: {e}")
            return None

    async def update_design_on_sheet(self, gang_sheet_id: str, design_id: str, design_updates: dict) -> Optional[GangSheet]:
        """Update a specific design on gang sheet"""
        if not ObjectId.is_valid(gang_sheet_id):
            return None

        gang_sheet = await self.get_gang_sheet_by_id(gang_sheet_id)
        if not gang_sheet:
            return None

        # Find and update the design
        for i, design in enumerate(gang_sheet.designs):
            if design.id == design_id:
                for key, value in design_updates.items():
                    if hasattr(design, key):
                        setattr(design, key, value)
                break
        else:
            return None  # Design not found

        gang_sheet.calculate_total_price()
        gang_sheet.updated_at = datetime.utcnow()

        # Update in database
        await self.collection.update_one(
            {"_id": ObjectId(gang_sheet_id)},
            {
                "$set": {
                    "designs": [design.dict() for design in gang_sheet.designs],
                    "total_price": gang_sheet.total_price,
                    "updated_at": gang_sheet.updated_at
                }
            }
        )

        return gang_sheet

    async def remove_design_from_sheet(self, gang_sheet_id: str, design_id: str) -> Optional[GangSheet]:
        """Remove a design from gang sheet"""
        if not ObjectId.is_valid(gang_sheet_id):
            return None

        gang_sheet = await self.get_gang_sheet_by_id(gang_sheet_id)
        if not gang_sheet:
            return None

        # Remove the design
        gang_sheet.designs = [d for d in gang_sheet.designs if d.id != design_id]
        gang_sheet.calculate_total_price()
        gang_sheet.updated_at = datetime.utcnow()

        # Update in database
        await self.collection.update_one(
            {"_id": ObjectId(gang_sheet_id)},
            {
                "$set": {
                    "designs": [design.dict() for design in gang_sheet.designs],
                    "total_price": gang_sheet.total_price,
                    "updated_at": gang_sheet.updated_at
                }
            }
        )

        return gang_sheet

    async def auto_nest_designs(self, gang_sheet_id: str) -> Optional[GangSheet]:
        """Auto-nest designs on gang sheet using simple bin packing algorithm"""
        if not ObjectId.is_valid(gang_sheet_id):
            return None

        gang_sheet = await self.get_gang_sheet_by_id(gang_sheet_id)
        if not gang_sheet or not gang_sheet.designs:
            return None

        # Simple bin packing algorithm
        sheet_width = gang_sheet.width * 72  # Convert to pixels
        sheet_height = gang_sheet.height * 72
        padding = 5
        
        current_x = padding
        current_y = padding
        row_height = 0

        optimized_designs = []
        for design in gang_sheet.designs:
            # Check if design fits in current row
            if current_x + design.width + padding > sheet_width:
                # Move to next row
                current_x = padding
                current_y += row_height + padding
                row_height = 0

            # Check if design fits vertically
            if current_y + design.height + padding <= sheet_height:
                optimized_design = design.copy()
                optimized_design.x = current_x
                optimized_design.y = current_y
                optimized_designs.append(optimized_design)

                current_x += design.width + padding
                row_height = max(row_height, design.height)

        gang_sheet.designs = optimized_designs
        gang_sheet.updated_at = datetime.utcnow()

        # Update in database
        await self.collection.update_one(
            {"_id": ObjectId(gang_sheet_id)},
            {
                "$set": {
                    "designs": [design.dict() for design in gang_sheet.designs],
                    "updated_at": gang_sheet.updated_at
                }
            }
        )

        return gang_sheet

    async def update_gang_sheet_status(self, gang_sheet_id: str, status: str) -> Optional[GangSheet]:
        """Update gang sheet status"""
        if not ObjectId.is_valid(gang_sheet_id):
            return None

        result = await self.collection.update_one(
            {"_id": ObjectId(gang_sheet_id)},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        if result.modified_count:
            return await self.get_gang_sheet_by_id(gang_sheet_id)
        return None

    def get_gang_sheet_templates(self) -> List[dict]:
        """Get available gang sheet templates"""
        return [
            {
                "id": "template_12x16",
                "name": "12x16 Standard Sheet",
                "width": 12,
                "height": 16,
                "price": 18.99,
                "max_designs": 50
            },
            {
                "id": "template_22x24",
                "name": "22x24 Large Sheet",
                "width": 22,
                "height": 24,
                "price": 45.99,
                "max_designs": 100
            },
            {
                "id": "template_8x11",
                "name": "8.5x11 Small Sheet",
                "width": 8.5,
                "height": 11,
                "price": 12.99,
                "max_designs": 25
            }
        ]


# Global service instance - will be initialized after database connection
gang_sheet_service = None

def get_gang_sheet_service():
    global gang_sheet_service
    if gang_sheet_service is None:
        gang_sheet_service = GangSheetService()
    return gang_sheet_service