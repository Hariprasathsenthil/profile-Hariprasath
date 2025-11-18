from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from app.models.user import User, UserCreate, UserRole, UserUpdate
from app.models.complaint import Department, ComplaintStatus
from app.models.escalation import EscalationRule
from app.middleware.auth_middleware import require_role
from app.database import get_users_collection, get_complaints_collection
from app.services.auth_service import create_user
from app.services.complaint_service import assign_officer_to_complaint
from app.services.escalation_service import (
    get_escalation_rules,
    create_or_update_escalation_rule
)
from app.utils.security import get_password_hash

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user_data: UserCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Create a new user (Admin only)"""
    user = await create_user(user_data)
    return {
        "message": "User created successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

@router.get("/users", response_model=List[User])
async def list_all_users(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Get all users (Admin and Manager only)"""
    users_collection = await get_users_collection()
    users_docs = await users_collection.find().to_list(length=None)
    
    return [
        User(
            id=str(doc["_id"]),
            email=doc["email"],
            full_name=doc["full_name"],
            role=doc["role"],
            created_at=doc["created_at"],
            is_active=doc.get("is_active", True)
        )
        for doc in users_docs
    ]

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Update user details (Admin only)"""
    users_collection = await get_users_collection()
    
    try:
        user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_dict = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
    
    # Hash password if provided
    if "password" in update_dict:
        update_dict["hashed_password"] = get_password_hash(update_dict.pop("password"))
    
    if update_dict:
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_dict}
        )
    
    updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
    
    return {
        "message": "User updated successfully",
        "user": {
            "id": str(updated_user["_id"]),
            "email": updated_user["email"],
            "full_name": updated_user["full_name"],
            "role": updated_user["role"]
        }
    }

@router.post("/assign-complaint")
async def assign_complaint(
    complaint_id: str,
    officer_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Assign a complaint to an officer"""
    users_collection = await get_users_collection()
    
    try:
        officer_doc = await users_collection.find_one({"_id": ObjectId(officer_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid officer ID")
    
    if not officer_doc:
        raise HTTPException(status_code=404, detail="Officer not found")
    
    if officer_doc["role"] not in [UserRole.OFFICER, UserRole.MANAGER]:
        raise HTTPException(status_code=400, detail="User is not an officer or manager")
    
    complaint = await assign_officer_to_complaint(
        complaint_id,
        str(officer_doc["_id"]),
        officer_doc["email"]
    )
    
    return {
        "message": "Complaint assigned successfully",
        "complaint": complaint
    }

@router.get("/statistics")
async def get_statistics(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Get complaint statistics for dashboard"""
    complaints_collection = await get_complaints_collection()
    
    # Total complaints
    total_complaints = await complaints_collection.count_documents({})
    
    # Complaints by status
    pending = await complaints_collection.count_documents({"status": ComplaintStatus.PENDING})
    in_progress = await complaints_collection.count_documents({"status": ComplaintStatus.IN_PROGRESS})
    resolved = await complaints_collection.count_documents({"status": ComplaintStatus.RESOLVED})
    escalated = await complaints_collection.count_documents({"status": ComplaintStatus.ESCALATED})
    
    # Complaints by department
    maintenance = await complaints_collection.count_documents({"department": Department.MAINTENANCE})
    it = await complaints_collection.count_documents({"department": Department.IT})
    administration = await complaints_collection.count_documents({"department": Department.ADMINISTRATION})
    
    # Recent complaints
    recent_complaints = await complaints_collection.find().sort("submission_date", -1).limit(10).to_list(length=10)
    
    return {
        "total_complaints": total_complaints,
        "by_status": {
            "pending": pending,
            "in_progress": in_progress,
            "resolved": resolved,
            "escalated": escalated
        },
        "by_department": {
            "maintenance": maintenance,
            "it": it,
            "administration": administration
        },
        "recent_complaints": [
            {
                "id": str(c["_id"]),
                "complaint_id": c["complaint_id"],
                "title": c["title"],
                "status": c["status"],
                "department": c["department"],
                "submission_date": c["submission_date"].isoformat()
            }
            for c in recent_complaints
        ]
    }

@router.get("/escalation-rules", response_model=List[EscalationRule])
async def list_escalation_rules(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Get all escalation rules"""
    return await get_escalation_rules()

@router.post("/escalation-rules")
async def set_escalation_rule(
    department: Department,
    time_limit_hours: int,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Create or update escalation rule for a department"""
    rule = await create_or_update_escalation_rule(department, time_limit_hours)
    return {
        "message": "Escalation rule updated successfully",
        "rule": rule
    }
