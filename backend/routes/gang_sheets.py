from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import List, Optional
from models.gang_sheet import GangSheet, GangSheetCreate, DesignUpload
from utils import get_gang_sheet_service
import base64

router = APIRouter(prefix="/gang-sheets", tags=["gang-sheets"])


@router.get("/templates")
async def get_gang_sheet_templates():
    """Get available gang sheet templates"""
    return get_gang_sheet_service().get_gang_sheet_templates()


@router.post("/", response_model=GangSheet)
async def create_gang_sheet(gang_sheet: GangSheetCreate):
    """Create a new gang sheet"""
    return await get_gang_sheet_service().create_gang_sheet(gang_sheet)


@router.get("/{gang_sheet_id}", response_model=GangSheet)
async def get_gang_sheet(gang_sheet_id: str):
    """Get a specific gang sheet by ID"""
    gang_sheet = await get_gang_sheet_service().get_gang_sheet_by_id(gang_sheet_id)
    if not gang_sheet:
        raise HTTPException(status_code=404, detail="Gang sheet not found")
    return gang_sheet


@router.get("/user/{user_id}", response_model=List[GangSheet])
async def get_user_gang_sheets(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get gang sheets for a specific user"""
    return await get_gang_sheet_service().get_gang_sheets_by_user(user_id, skip, limit)


@router.post("/{gang_sheet_id}/designs", response_model=GangSheet)
async def add_design_to_gang_sheet(gang_sheet_id: str, design: DesignUpload):
    """Add a design to gang sheet"""
    updated_sheet = await get_gang_sheet_service().add_design_to_sheet(gang_sheet_id, design)
    if not updated_sheet:
        raise HTTPException(status_code=404, detail="Gang sheet not found or error processing design")
    return updated_sheet


@router.post("/{gang_sheet_id}/designs/upload", response_model=GangSheet)
async def upload_design_file(gang_sheet_id: str, file: UploadFile = File(...)):
    """Upload design file to gang sheet"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read file and convert to base64
    file_content = await file.read()
    file_base64 = base64.b64encode(file_content).decode('utf-8')
    file_data_url = f"data:{file.content_type};base64,{file_base64}"
    
    design = DesignUpload(
        name=file.filename,
        file_data=file_data_url,
        x=50.0,
        y=50.0,
        quantity=1
    )
    
    updated_sheet = await get_gang_sheet_service().add_design_to_sheet(gang_sheet_id, design)
    if not updated_sheet:
        raise HTTPException(status_code=404, detail="Gang sheet not found or error processing design")
    return updated_sheet


@router.put("/{gang_sheet_id}/designs/{design_id}", response_model=GangSheet)
async def update_design_on_gang_sheet(gang_sheet_id: str, design_id: str, updates: dict):
    """Update a design on gang sheet"""
    updated_sheet = await get_gang_sheet_service().update_design_on_sheet(gang_sheet_id, design_id, updates)
    if not updated_sheet:
        raise HTTPException(status_code=404, detail="Gang sheet or design not found")
    return updated_sheet


@router.delete("/{gang_sheet_id}/designs/{design_id}", response_model=GangSheet)
async def remove_design_from_gang_sheet(gang_sheet_id: str, design_id: str):
    """Remove a design from gang sheet"""
    updated_sheet = await get_gang_sheet_service().remove_design_from_sheet(gang_sheet_id, design_id)
    if not updated_sheet:
        raise HTTPException(status_code=404, detail="Gang sheet or design not found")
    return updated_sheet


@router.post("/{gang_sheet_id}/auto-nest", response_model=GangSheet)
async def auto_nest_gang_sheet(gang_sheet_id: str):
    """Auto-nest designs on gang sheet"""
    updated_sheet = await get_gang_sheet_service().auto_nest_designs(gang_sheet_id)
    if not updated_sheet:
        raise HTTPException(status_code=404, detail="Gang sheet not found")
    return updated_sheet


@router.put("/{gang_sheet_id}/status")
async def update_gang_sheet_status(gang_sheet_id: str, status: str):
    """Update gang sheet status"""
    valid_statuses = ["draft", "ordered", "processing", "completed"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    updated_sheet = await get_gang_sheet_service().update_gang_sheet_status(gang_sheet_id, status)
    if not updated_sheet:
        raise HTTPException(status_code=404, detail="Gang sheet not found")
    return {"message": f"Gang sheet status updated to {status}"}