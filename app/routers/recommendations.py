from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.item import ItemType
from app.services.recommendation_service import get_personalized_recommendations, generate_hybrid_recommendations
from app.services.collaborative_filtering import generate_collaborative_recommendations
from app.services.content_based import generate_content_based_recommendations
from app.services.popular_recommendations import get_popular_items, get_trending_items


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/personalized", response_model=List[dict])
async def get_personalized_recommendations_endpoint(
    method: str = Query("hybrid", regex="^(hybrid|collaborative|content)$"),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get personalized recommendations for the current user"""
    
    try:
        recommendations = await get_personalized_recommendations(
            db, current_user.id, limit=limit, method=method
        )
        
        if len(recommendations) == 0:
            recommendations = await get_popular_items(
                db, limit=limit, min_ratings=1
            )
        
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.get("/hybrid", response_model=List[dict])
async def get_hybrid_recommendations(
    limit: int = Query(10, ge=1, le=100),
    collaborative_weight: float = Query(0.6, ge=0.0, le=1.0),
    content_weight: float = Query(0.4, ge=0.0, le=1.0),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get hybrid recommendations combining collaborative and content-based filtering"""
    
    if abs(collaborative_weight + content_weight - 1.0) > 0.01:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Weights must sum to 1.0"
        )
    
    try:
        recommendations = await generate_hybrid_recommendations(
            db,
            current_user.id,
            limit=limit,
            collaborative_weight=collaborative_weight,
            content_weight=content_weight
        )
        
        if len(recommendations) == 0:
            recommendations = await get_popular_items(
                db, limit=limit, min_ratings=1
            )
        
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating hybrid recommendations: {str(e)}"
        )


@router.get("/popular", response_model=List[dict])
async def get_popular_recommendations(
    item_type: Optional[ItemType] = Query(None),
    category: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    min_ratings: int = Query(1, ge=1),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get popular items based on ratings"""
    
    try:
        recommendations = await get_popular_items(
            db,
            item_type=item_type,
            category=category,
            genre=genre,
            limit=limit,
            min_ratings=min_ratings
        )
        
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating popular recommendations: {str(e)}"
        )


@router.get("/trending", response_model=List[dict])
async def get_trending_recommendations(
    item_type: Optional[ItemType] = Query(None),
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get trending items based on recent ratings"""
    
    try:
        recommendations = await get_trending_items(
            db,
            item_type=item_type,
            days=days,
            limit=limit
        )
        
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating trending recommendations: {str(e)}"
        )


@router.get("/collaborative", response_model=List[dict])
async def get_collaborative_recommendations(
    limit: int = Query(10, ge=1, le=100),
    min_similarity: float = Query(0.3, ge=0.0, le=1.0),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get recommendations using collaborative filtering"""
    
    try:
        recommendations = await generate_collaborative_recommendations(
            db,
            current_user.id,
            limit=limit,
            min_similarity=min_similarity
        )
        
        if len(recommendations) == 0:
            recommendations = await get_popular_items(
                db, limit=limit, min_ratings=1
            )
        
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating collaborative recommendations: {str(e)}"
        )


@router.get("/content-based", response_model=List[dict])
async def get_content_based_recommendations(
    limit: int = Query(10, ge=1, le=100),
    min_similarity: float = Query(0.3, ge=0.0, le=1.0),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get recommendations using content-based filtering"""
    
    try:
        recommendations = await generate_content_based_recommendations(
            db,
            current_user.id,
            limit=limit,
            min_similarity=min_similarity
        )
        
        if len(recommendations) == 0:
            recommendations = await get_popular_items(
                db, limit=limit, min_ratings=1
            )
        
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating content-based recommendations: {str(e)}"
        )

