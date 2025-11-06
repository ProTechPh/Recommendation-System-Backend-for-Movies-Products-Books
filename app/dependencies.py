from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_database
from app.models.user import User
from app.services.auth_service import get_current_user_from_token, create_anonymous_user

bearer_scheme = HTTPBearer(bearerFormat="JWT", scheme_name="Bearer", auto_error=False)


async def get_db() -> AsyncIOMotorDatabase:
    """Dependency to get database instance"""
    from app.database import get_database
    return await get_database()


async def get_current_user(
    db: AsyncIOMotorDatabase = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> User:
    """Dependency to get current authenticated user (supports anonymous)"""
    if credentials is None:
        return await create_anonymous_user(db)
    
    token = credentials.credentials
    user = await get_current_user_from_token(db, token)
    if user is None:
        return await create_anonymous_user(db)
    
    return user


async def get_current_authenticated_user(
    db: AsyncIOMotorDatabase = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> User:
    """Dependency to get current authenticated user (required, non-anonymous)"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    user = await get_current_user_from_token(db, token)
    if user is None or user.is_anonymous:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
