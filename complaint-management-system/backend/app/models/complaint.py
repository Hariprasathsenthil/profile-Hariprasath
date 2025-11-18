from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class Department(str, Enum):
    MAINTENANCE = "Maintenance"
    IT = "IT"
    ADMINISTRATION = "Administration"

class ComplaintStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In-Progress"
    RESOLVED = "Resolved"
    ESCALATED = "Escalated"

class ComplaintBase(BaseModel):
    title: str
    description: str
    department: Department

class ComplaintCreate(ComplaintBase):
    pass

class ComplaintUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[Department] = None
    status: Optional[ComplaintStatus] = None
    assigned_officer_id: Optional[str] = None
    resolution_notes: Optional[str] = None

class ComplaintInDB(ComplaintBase):
    id: str = Field(alias="_id")
    complaint_id: str
    user_id: str
    user_email: str
    status: ComplaintStatus
    submission_date: datetime
    last_updated: datetime
    assigned_officer_id: Optional[str] = None
    assigned_officer_email: Optional[str] = None
    resolution_notes: Optional[str] = None
    escalation_count: int = 0
    
    class Config:
        populate_by_name = True

class Complaint(ComplaintBase):
    id: str
    complaint_id: str
    user_id: str
    user_email: str
    status: ComplaintStatus
    submission_date: datetime
    last_updated: datetime
    assigned_officer_id: Optional[str] = None
    assigned_officer_email: Optional[str] = None
    resolution_notes: Optional[str] = None
    escalation_count: int = 0
