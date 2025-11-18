from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from app.models.complaint import ComplaintCreate, ComplaintUpdate, Complaint
from app.models.user import User, UserRole
from app.middleware.auth_middleware import get_current_active_user, require_role
from app.services.complaint_service import (
    create_complaint,
    get_user_complaints,
    get_all_complaints,
    get_complaint_by_id,
    update_complaint
)

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])

@router.post("/", response_model=Complaint)
async def submit_complaint(
    complaint_data: ComplaintCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Submit a new complaint"""
    return await create_complaint(complaint_data, current_user)

@router.get("/my-complaints", response_model=List[Complaint])
async def get_my_complaints(current_user: User = Depends(get_current_active_user)):
    """Get all complaints submitted by the current user"""
    return await get_user_complaints(current_user.id)

@router.get("/all", response_model=List[Complaint])
async def list_all_complaints(
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(require_role([UserRole.OFFICER, UserRole.MANAGER, UserRole.ADMIN]))
):
    """Get all complaints (for officers, managers, and admins)"""
    return await get_all_complaints(status, department, skip, limit)

@router.get("/{complaint_id}", response_model=Complaint)
async def get_complaint(
    complaint_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific complaint by ID"""
    complaint = await get_complaint_by_id(complaint_id)
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Check if user has permission to view this complaint
    if current_user.role not in [UserRole.OFFICER, UserRole.MANAGER, UserRole.ADMIN]:
        if complaint.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this complaint")
    
    return complaint

@router.put("/{complaint_id}", response_model=Complaint)
async def update_complaint_status(
    complaint_id: str,
    update_data: ComplaintUpdate,
    current_user: User = Depends(require_role([UserRole.OFFICER, UserRole.MANAGER, UserRole.ADMIN]))
):
    """Update complaint status and details (for officers, managers, and admins)"""
    return await update_complaint(complaint_id, update_data, current_user)
