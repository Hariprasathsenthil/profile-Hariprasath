from datetime import datetime
import random
import string

def generate_complaint_id() -> str:
    """Generate a unique complaint ID in format: CMP-YYYYMMDD-XXXX"""
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"CMP-{date_str}-{random_str}"

def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable format"""
    if doc is None:
        return None
    
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    
    for key, value in doc.items():
        if isinstance(value, datetime):
            doc[key] = value.isoformat()
    
    return doc
