from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.dependencies import get_db, get_current_authenticated_user
from app.models.user import User, UserUpdate
from app.services.auth_service import get_user_by_id
from bson import ObjectId


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
async def get_my_profile(current_user: User = Depends(get_current_authenticated_user)):
    """Get current user's profile"""
    return current_user


@router.put("/me", response_model=User)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_authenticated_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update current user's profile"""
    update_data = {}
    if user_update.username is not None:
        update_data["username"] = user_update.username
    if user_update.preferences is not None:
        update_data["preferences"] = user_update.preferences
    
    if not update_data:
        return current_user
    
    await db.users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": update_data}
    )
    
    updated_user = await get_user_by_id(db, current_user.id)
    return updated_user

