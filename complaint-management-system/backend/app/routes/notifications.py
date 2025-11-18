from fastapi import APIRouter, Depends
from typing import List
from app.models.user import User
from app.models.notification import Notification
from app.middleware.auth_middleware import get_current_active_user
from app.database import get_notifications_collection
from bson import ObjectId

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.get("/", response_model=List[Notification])
async def get_user_notifications(
    current_user: User = Depends(get_current_active_user)
):
    """Get all notifications for the current user"""
    notifications_collection = await get_notifications_collection()
    notifications = await notifications_collection.find(
        {"user_id": current_user.id}
    ).sort("created_at", -1).to_list(length=100)
    
    return [
        Notification(
            id=str(n["_id"]),
            user_id=n["user_id"],
            complaint_id=n["complaint_id"],
            type=n["type"],
            message=n["message"],
            is_read=n["is_read"],
            created_at=n["created_at"]
        )
        for n in notifications
    ]

@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Mark a notification as read"""
    notifications_collection = await get_notifications_collection()
    
    result = await notifications_collection.update_one(
        {"_id": ObjectId(notification_id), "user_id": current_user.id},
        {"$set": {"is_read": True}}
    )
    
    if result.modified_count == 0:
        return {"message": "Notification not found or already read"}
    
    return {"message": "Notification marked as read"}

@router.put("/mark-all-read")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_active_user)
):
    """Mark all notifications as read for the current user"""
    notifications_collection = await get_notifications_collection()
    
    result = await notifications_collection.update_many(
        {"user_id": current_user.id, "is_read": False},
        {"$set": {"is_read": True}}
    )
    
    return {
        "message": f"Marked {result.modified_count} notifications as read"
    }
