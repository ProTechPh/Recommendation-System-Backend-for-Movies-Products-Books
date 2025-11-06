from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.rating import RatingCreate, RatingUpdate, Rating, UserRating, ItemRating


router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.post("", response_model=Rating, status_code=status.HTTP_201_CREATED)
async def create_rating(
    rating: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create or update a rating for an item"""
    if not ObjectId.is_valid(rating.item_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID"
        )
    
    item = await db.items.find_one({"_id": ObjectId(rating.item_id)})
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    existing_rating = await db.ratings.find_one({
        "user_id": current_user.id,
        "item_id": rating.item_id
    })
    
    if existing_rating:
        update_data = {
            "rating": rating.rating,
            "updated_at": datetime.utcnow()
        }
        await db.ratings.update_one(
            {"_id": existing_rating["_id"]},
            {"$set": update_data}
        )
        existing_rating.update(update_data)
        existing_rating["id"] = str(existing_rating["_id"])
        return Rating(**existing_rating)
    
    rating_dict = {
        "user_id": current_user.id,
        "item_id": rating.item_id,
        "rating": rating.rating,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.ratings.insert_one(rating_dict)
    rating_dict["id"] = str(result.inserted_id)
    return Rating(**rating_dict)


@router.get("/user/{user_id}", response_model=List[UserRating])
async def get_user_ratings(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all ratings by a specific user"""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    cursor = db.ratings.find({"user_id": user_id}).skip(skip).limit(limit).sort("created_at", -1)
    ratings = await cursor.to_list(length=limit)
    
    result = []
    for rating in ratings:
        rating_dict = {**rating, "id": str(rating["_id"])}
        item = await db.items.find_one({"_id": ObjectId(rating["item_id"])})
        if item:
            rating_dict["item_title"] = item.get("title")
            rating_dict["item_name"] = item.get("name")
        result.append(UserRating(**rating_dict))
    
    return result


@router.get("/item/{item_id}", response_model=List[ItemRating])
async def get_item_ratings(
    item_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all ratings for a specific item"""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID"
        )
    
    cursor = db.ratings.find({"item_id": item_id}).skip(skip).limit(limit).sort("created_at", -1)
    ratings = await cursor.to_list(length=limit)
    
    result = []
    for rating in ratings:
        rating_dict = {**rating, "id": str(rating["_id"])}
        user = await db.users.find_one({"_id": ObjectId(rating["user_id"])})
        if user:
            rating_dict["username"] = user.get("username")
        result.append(ItemRating(**rating_dict))
    
    return result


@router.get("/me", response_model=List[UserRating])
async def get_my_ratings(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get current user's ratings"""
    return await get_user_ratings(current_user.id, skip, limit, db)


@router.put("/{rating_id}", response_model=Rating)
async def update_rating(
    rating_id: str,
    rating_update: RatingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update a rating"""
    if not ObjectId.is_valid(rating_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid rating ID"
        )
    
    rating = await db.ratings.find_one({"_id": ObjectId(rating_id)})
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    
    if rating["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this rating"
        )
    
    update_data = {
        "rating": rating_update.rating,
        "updated_at": datetime.utcnow()
    }
    
    await db.ratings.update_one(
        {"_id": ObjectId(rating_id)},
        {"$set": update_data}
    )
    
    rating.update(update_data)
    rating["id"] = str(rating["_id"])
    return Rating(**rating)


@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(
    rating_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete a rating"""
    if not ObjectId.is_valid(rating_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid rating ID"
        )
    
    rating = await db.ratings.find_one({"_id": ObjectId(rating_id)})
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    
    if rating["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this rating"
        )
    
    await db.ratings.delete_one({"_id": ObjectId(rating_id)})
    return None
