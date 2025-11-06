from datetime import datetime, timedelta
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from fastapi import HTTPException, status
from app.models.user import UserCreate, UserInDB, User, Token
from app.utils.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.config import settings


async def create_user(db: AsyncIOMotorDatabase, user: UserCreate) -> User:
    """Create a new user"""
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = await db.users.find_one({"username": user.username})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    hashed_password = get_password_hash(user.password)
    user_dict = {
        "email": user.email,
        "username": user.username,
        "hashed_password": hashed_password,
        "preferences": user.preferences or {},
        "is_active": True,
        "created_at": datetime.utcnow(),
        "is_anonymous": False
    }
    
    result = await db.users.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    user_dict.pop("hashed_password", None)
    
    return User(**user_dict)


async def authenticate_user(db: AsyncIOMotorDatabase, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password"""
    user = await db.users.find_one({"email": email})
    if not user:
        return None
    
    if not verify_password(password, user["hashed_password"]):
        return None
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    user["id"] = str(user["_id"])
    user.pop("hashed_password", None)
    user.pop("_id", None)
    
    return User(**user)


async def create_anonymous_user(db: AsyncIOMotorDatabase) -> User:
    """Create an anonymous user session"""
    user_dict = {
        "email": f"anonymous_{ObjectId()}@anonymous.local",
        "username": f"anonymous_{ObjectId()}",
        "hashed_password": "",
        "preferences": {},
        "is_active": True,
        "created_at": datetime.utcnow(),
        "is_anonymous": True
    }
    
    result = await db.users.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    user_dict.pop("hashed_password", None)
    
    return User(**user_dict)


async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str) -> Optional[User]:
    """Get a user by ID"""
    if not ObjectId.is_valid(user_id):
        return None
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None
    
    user["id"] = str(user["_id"])
    user.pop("hashed_password", None)
    user.pop("_id", None)
    
    return User(**user)


async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[User]:
    """Get a user by email"""
    user = await db.users.find_one({"email": email})
    if not user:
        return None
    
    user["id"] = str(user["_id"])
    user.pop("hashed_password", None)
    user.pop("_id", None)
    
    return User(**user)


async def login_user(db: AsyncIOMotorDatabase, email: str, password: str) -> Token:
    """Login a user and return access token"""
    user = await authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id, "is_anonymous": user.is_anonymous},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token)


async def get_current_user_from_token(db: AsyncIOMotorDatabase, token: str) -> Optional[User]:
    """Get current user from JWT token"""
    payload = decode_access_token(token)
    if payload is None:
        return None
    
    user_id: str = payload.get("sub")
    if user_id is None:
        return None
    
    user = await get_user_by_id(db, user_id)
    return user
