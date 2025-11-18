from datetime import datetime
from typing import Optional, List
from fastapi import HTTPException, status
from bson import ObjectId
from app.database import get_complaints_collection, get_notifications_collection
from app.models.complaint import ComplaintCreate, ComplaintUpdate, Complaint, ComplaintStatus
from app.models.user import User
from app.utils.helpers import generate_complaint_id

async def create_complaint(complaint_data: ComplaintCreate, user: User) -> Complaint:
    complaints_collection = await get_complaints_collection()
    
    complaint_doc = {
        "complaint_id": generate_complaint_id(),
        "user_id": user.id,
        "user_email": user.email,
        "title": complaint_data.title,
        "description": complaint_data.description,
        "department": complaint_data.department,
        "status": ComplaintStatus.PENDING,
        "submission_date": datetime.utcnow(),
        "last_updated": datetime.utcnow(),
        "assigned_officer_id": None,
        "assigned_officer_email": None,
        "resolution_notes": None,
        "escalation_count": 0
    }
    
    result = await complaints_collection.insert_one(complaint_doc)
    
    # Create notification
    await create_notification(
        user.id,
        str(result.inserted_id),
        "complaint_submitted",
        f"Your complaint '{complaint_data.title}' has been submitted successfully."
    )
    
    complaint_doc["_id"] = result.inserted_id
    return complaint_doc_to_model(complaint_doc)

async def get_user_complaints(user_id: str) -> List[Complaint]:
    complaints_collection = await get_complaints_collection()
    cursor = complaints_collection.find({"user_id": user_id}).sort("submission_date", -1)
    complaints = await cursor.to_list(length=None)
    return [complaint_doc_to_model(doc) for doc in complaints]

async def get_all_complaints(
    status: Optional[str] = None,
    department: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Complaint]:
    complaints_collection = await get_complaints_collection()
    
    query = {}
    if status:
        query["status"] = status
    if department:
        query["department"] = department
    
    cursor = complaints_collection.find(query).sort("submission_date", -1).skip(skip).limit(limit)
    complaints = await cursor.to_list(length=None)
    return [complaint_doc_to_model(doc) for doc in complaints]

async def get_complaint_by_id(complaint_id: str) -> Optional[Complaint]:
    complaints_collection = await get_complaints_collection()
    
    try:
        complaint_doc = await complaints_collection.find_one({"_id": ObjectId(complaint_id)})
    except:
        complaint_doc = await complaints_collection.find_one({"complaint_id": complaint_id})
    
    if not complaint_doc:
        return None
    
    return complaint_doc_to_model(complaint_doc)

async def update_complaint(complaint_id: str, update_data: ComplaintUpdate, user: User) -> Complaint:
    complaints_collection = await get_complaints_collection()
    
    complaint = await get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    update_dict = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
    update_dict["last_updated"] = datetime.utcnow()
    
    await complaints_collection.update_one(
        {"_id": ObjectId(complaint.id)},
        {"$set": update_dict}
    )
    
    # Create notification for status change
    if "status" in update_dict:
        await create_notification(
            complaint.user_id,
            complaint.id,
            "complaint_updated",
            f"Your complaint '{complaint.title}' status has been updated to {update_dict['status']}."
        )
    
    updated_complaint = await get_complaint_by_id(complaint_id)
    return updated_complaint

async def assign_officer_to_complaint(complaint_id: str, officer_id: str, officer_email: str) -> Complaint:
    complaints_collection = await get_complaints_collection()
    
    complaint = await get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    await complaints_collection.update_one(
        {"_id": ObjectId(complaint.id)},
        {
            "$set": {
                "assigned_officer_id": officer_id,
                "assigned_officer_email": officer_email,
                "status": ComplaintStatus.IN_PROGRESS,
                "last_updated": datetime.utcnow()
            }
        }
    )
    
    # Notify user
    await create_notification(
        complaint.user_id,
        complaint.id,
        "complaint_assigned",
        f"Your complaint '{complaint.title}' has been assigned to an officer."
    )
    
    # Notify officer
    await create_notification(
        officer_id,
        complaint.id,
        "complaint_assigned",
        f"You have been assigned to complaint '{complaint.title}'."
    )
    
    return await get_complaint_by_id(complaint_id)

async def create_notification(user_id: str, complaint_id: str, notification_type: str, message: str):
    notifications_collection = await get_notifications_collection()
    
    notification_doc = {
        "user_id": user_id,
        "complaint_id": complaint_id,
        "type": notification_type,
        "message": message,
        "is_read": False,
        "created_at": datetime.utcnow()
    }
    
    await notifications_collection.insert_one(notification_doc)

def complaint_doc_to_model(doc: dict) -> Complaint:
    return Complaint(
        id=str(doc["_id"]),
        complaint_id=doc["complaint_id"],
        user_id=doc["user_id"],
        user_email=doc["user_email"],
        title=doc["title"],
        description=doc["description"],
        department=doc["department"],
        status=doc["status"],
        submission_date=doc["submission_date"],
        last_updated=doc["last_updated"],
        assigned_officer_id=doc.get("assigned_officer_id"),
        assigned_officer_email=doc.get("assigned_officer_email"),
        resolution_notes=doc.get("resolution_notes"),
        escalation_count=doc.get("escalation_count", 0)
    )
