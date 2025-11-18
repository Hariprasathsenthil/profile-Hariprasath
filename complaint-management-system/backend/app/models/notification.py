from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NotificationType(str):
    COMPLAINT_SUBMITTED = "complaint_submitted"
    COMPLAINT_ASSIGNED = "complaint_assigned"
    COMPLAINT_UPDATED = "complaint_updated"
    COMPLAINT_RESOLVED = "complaint_resolved"
    COMPLAINT_ESCALATED = "complaint_escalated"

class Notification(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    complaint_id: str
    type: str
    message: str
    is_read: bool = False
    created_at: datetime
    
    class Config:
        populate_by_name = True
