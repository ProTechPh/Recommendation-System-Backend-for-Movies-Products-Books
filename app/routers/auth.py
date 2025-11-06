from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.dependencies import get_db, get_current_authenticated_user
from app.models.user import UserCreate, User, Token
from app.services.auth_service import create_user, login_user


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Register a new user"""
    return await create_user(db, user)


@router.post("/login", response_model=Token)
async def login(email: str, password: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Login and get access token"""
    return await login_user(db, email, password)


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_authenticated_user)):
    """Get current user information"""
    return current_user
