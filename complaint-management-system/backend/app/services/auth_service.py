from datetime import datetime
from fastapi import HTTPException, status
from app.database import get_users_collection
from app.models.user import UserCreate, User, UserRole
from app.utils.security import get_password_hash, verify_password, create_access_token
from bson import ObjectId

async def create_user(user_data: UserCreate) -> User:
    users_collection = await get_users_collection()
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user document
    user_doc = {
        "email": user_data.email,
        "full_name": user_data.full_name,
        "role": user_data.role,
        "hashed_password": get_password_hash(user_data.password),
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    result = await users_collection.insert_one(user_doc)
    
    return User(
        id=str(result.inserted_id),
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        created_at=user_doc["created_at"],
        is_active=True
    )

async def authenticate_user(email: str, password: str):
    users_collection = await get_users_collection()
    user_doc = await users_collection.find_one({"email": email})
    
    if not user_doc:
        return None
    
    if not verify_password(password, user_doc["hashed_password"]):
        return None
    
    return user_doc

async def login_user(email: str, password: str):
    user = await authenticate_user(email, password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    }
