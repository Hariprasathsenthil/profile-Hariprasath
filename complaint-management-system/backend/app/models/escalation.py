from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.complaint import Department

class EscalationRule(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    department: Department
    time_limit_hours: int
    created_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True

class EscalationHistory(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    complaint_id: str
    escalated_at: datetime
    escalation_level: int
    reason: str
    notified_users: list[str] = []
    
    class Config:
        populate_by_name = True
