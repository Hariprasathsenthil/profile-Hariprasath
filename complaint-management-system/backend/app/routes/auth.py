from fastapi import APIRouter, HTTPException, status
from app.models.user import UserCreate, Token
from app.services.auth_service import create_user, login_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    user = await create_user(user_data)
    return {
        "message": "User registered successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

@router.post("/login", response_model=Token)
async def login(email: str, password: str):
    """Login user and return JWT token"""
    return await login_user(email, password)
