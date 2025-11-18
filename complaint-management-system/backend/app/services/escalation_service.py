from datetime import datetime, timedelta
from typing import List
from app.database import (
    get_complaints_collection,
    get_escalation_rules_collection,
    get_escalation_history_collection,
    get_users_collection,
    get_notifications_collection
)
from app.models.complaint import ComplaintStatus, Department
from app.models.escalation import EscalationRule
from bson import ObjectId

async def check_and_escalate_complaints():
    """Background job to check and escalate complaints"""
    complaints_collection = await get_complaints_collection()
    escalation_rules_collection = await get_escalation_rules_collection()
    escalation_history_collection = await get_escalation_history_collection()
    notifications_collection = await get_notifications_collection()
    users_collection = await get_users_collection()
    
    # Get all pending and in-progress complaints
    complaints = await complaints_collection.find({
        "status": {"$in": [ComplaintStatus.PENDING, ComplaintStatus.IN_PROGRESS]}
    }).to_list(length=None)
    
    for complaint in complaints:
        # Get escalation rule for department
        rule = await escalation_rules_collection.find_one({
            "department": complaint["department"]
        })
        
        if not rule:
            continue
        
        time_limit_hours = rule["time_limit_hours"]
        submission_date = complaint["submission_date"]
        time_elapsed = datetime.utcnow() - submission_date
        
        # Check if complaint should be escalated
        if time_elapsed > timedelta(hours=time_limit_hours):
            escalation_count = complaint.get("escalation_count", 0) + 1
            
            # Update complaint status
            await complaints_collection.update_one(
                {"_id": complaint["_id"]},
                {
                    "$set": {
                        "status": ComplaintStatus.ESCALATED,
                        "escalation_count": escalation_count,
                        "last_updated": datetime.utcnow()
                    }
                }
            )
            
            # Create escalation history
            escalation_doc = {
                "complaint_id": str(complaint["_id"]),
                "escalated_at": datetime.utcnow(),
                "escalation_level": escalation_count,
                "reason": f"Complaint unresolved for {time_limit_hours} hours",
                "notified_users": []
            }
            
            # Notify user
            user_notification = {
                "user_id": complaint["user_id"],
                "complaint_id": str(complaint["_id"]),
                "type": "complaint_escalated",
                "message": f"Your complaint '{complaint['title']}' has been escalated to management.",
                "is_read": False,
                "created_at": datetime.utcnow()
            }
            await notifications_collection.insert_one(user_notification)
            escalation_doc["notified_users"].append(complaint["user_id"])
            
            # Notify managers
            managers = await users_collection.find({"role": "Manager"}).to_list(length=None)
            for manager in managers:
                manager_notification = {
                    "user_id": str(manager["_id"]),
                    "complaint_id": str(complaint["_id"]),
                    "type": "complaint_escalated",
                    "message": f"Complaint '{complaint['title']}' in {complaint['department']} department has been escalated.",
                    "is_read": False,
                    "created_at": datetime.utcnow()
                }
                await notifications_collection.insert_one(manager_notification)
                escalation_doc["notified_users"].append(str(manager["_id"]))
            
            # Notify admins
            admins = await users_collection.find({"role": "Admin"}).to_list(length=None)
            for admin in admins:
                admin_notification = {
                    "user_id": str(admin["_id"]),
                    "complaint_id": str(complaint["_id"]),
                    "type": "complaint_escalated",
                    "message": f"Complaint '{complaint['title']}' in {complaint['department']} department has been escalated.",
                    "is_read": False,
                    "created_at": datetime.utcnow()
                }
                await notifications_collection.insert_one(admin_notification)
                escalation_doc["notified_users"].append(str(admin["_id"]))
            
            await escalation_history_collection.insert_one(escalation_doc)
            
            print(f"Escalated complaint {complaint['complaint_id']} - Level {escalation_count}")

async def get_escalation_rules() -> List[EscalationRule]:
    """Get all escalation rules"""
    escalation_rules_collection = await get_escalation_rules_collection()
    rules = await escalation_rules_collection.find().to_list(length=None)
    return [
        EscalationRule(
            id=str(rule["_id"]),
            department=rule["department"],
            time_limit_hours=rule["time_limit_hours"],
            created_at=rule.get("created_at")
        )
        for rule in rules
    ]

async def create_or_update_escalation_rule(department: Department, time_limit_hours: int) -> EscalationRule:
    """Create or update escalation rule for a department"""
    escalation_rules_collection = await get_escalation_rules_collection()
    
    existing_rule = await escalation_rules_collection.find_one({"department": department})
    
    if existing_rule:
        await escalation_rules_collection.update_one(
            {"department": department},
            {"$set": {"time_limit_hours": time_limit_hours}}
        )
        rule_id = str(existing_rule["_id"])
    else:
        rule_doc = {
            "department": department,
            "time_limit_hours": time_limit_hours,
            "created_at": datetime.utcnow()
        }
        result = await escalation_rules_collection.insert_one(rule_doc)
        rule_id = str(result.inserted_id)
    
    return EscalationRule(
        id=rule_id,
        department=department,
        time_limit_hours=time_limit_hours,
        created_at=datetime.utcnow()
    )

async def initialize_default_escalation_rules():
    """Initialize default escalation rules if they don't exist"""
    default_rules = [
        {"department": Department.MAINTENANCE, "time_limit_hours": 48},
        {"department": Department.IT, "time_limit_hours": 24},
        {"department": Department.ADMINISTRATION, "time_limit_hours": 72}
    ]
    
    for rule in default_rules:
        await create_or_update_escalation_rule(rule["department"], rule["time_limit_hours"])
