from typing import List, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models.item import ItemType


async def get_popular_items(
    db: AsyncIOMotorDatabase,
    item_type: Optional[ItemType] = None,
    category: Optional[str] = None,
    genre: Optional[str] = None,
    limit: int = 10,
    min_ratings: int = 1
) -> List[Dict]:
    """Get popular items based on ratings and interactions"""
    
    pipeline = []
    
    match_filter = {}
    if item_type:
        match_filter["item_type"] = item_type.value
    if category:
        match_filter["category"] = category
    if genre:
        match_filter["genres"] = genre
    
    if match_filter:
        pipeline.append({"$match": match_filter})
    
    pipeline.append({
        "$lookup": {
            "from": "ratings",
            "localField": "_id",
            "foreignField": "item_id",
            "as": "ratings"
        }
    })
    
    pipeline.append({
        "$match": {
            "$expr": {"$gte": [{"$size": "$ratings"}, min_ratings]}
        }
    })
    
    pipeline.append({
        "$addFields": {
            "avg_rating": {"$avg": "$ratings.rating"},
            "rating_count": {"$size": "$ratings"}
        }
    })
    
    pipeline.append({
        "$addFields": {
            "popularity_score": {
                "$multiply": [
                    "$avg_rating",
                    {"$add": [1, {"$multiply": [0.1, "$rating_count"]}]}
                ]
            }
        }
    })
    
    pipeline.append({
        "$sort": {"popularity_score": -1}
    })
    
    pipeline.append({
        "$limit": limit
    })
    
    pipeline.append({
        "$project": {
            "_id": 1,
            "item_type": 1,
            "title": 1,
            "name": 1,
            "description": 1,
            "genres": 1,
            "tags": 1,
            "metadata": 1,
            "created_at": 1,
            "updated_at": 1,
            "avg_rating": 1,
            "rating_count": 1,
            "popularity_score": 1
        }
    })
    
    items = await db.items.aggregate(pipeline).to_list(length=limit)
    
    result = []
    for item in items:
        item["id"] = str(item["_id"])
        item["recommendation_score"] = item.get("popularity_score", 0)
        item["recommendation_type"] = "popular"
        item["avg_rating"] = round(item.get("avg_rating", 0), 2)
        result.append(item)
    
    return result


async def get_popular_by_category(
    db: AsyncIOMotorDatabase,
    item_type: ItemType,
    limit_per_category: int = 5
) -> Dict[str, List[Dict]]:
    """Get popular items grouped by category/genre"""
    
    items = await db.items.find({"item_type": item_type.value}).to_list(length=None)
    
    categories = set()
    for item in items:
        if item_type == ItemType.PRODUCT and item.get("category"):
            categories.add(item["category"])
        elif item.get("genres"):
            categories.update(item["genres"])
    
    result = {}
    
    for category in categories:
        if item_type == ItemType.PRODUCT:
            popular = await get_popular_items(
                db, item_type=item_type, category=category, limit=limit_per_category
            )
        else:
            popular = await get_popular_items(
                db, item_type=item_type, genre=category, limit=limit_per_category
            )
        result[category] = popular
    
    return result


async def get_trending_items(
    db: AsyncIOMotorDatabase,
    item_type: Optional[ItemType] = None,
    days: int = 7,
    limit: int = 10
) -> List[Dict]:
    """Get trending items based on recent ratings"""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    pipeline = []
    
    match_filter = {}
    if item_type:
        match_filter["item_type"] = item_type.value
    
    if match_filter:
        pipeline.append({"$match": match_filter})
    
    pipeline.append({
        "$lookup": {
            "from": "ratings",
            "let": {"item_id": {"$toString": "$_id"}},
            "pipeline": [
                {
                    "$match": {
                        "$expr": {
                            "$and": [
                                {"$eq": ["$item_id", "$$item_id"]},
                                {"$gte": ["$created_at", cutoff_date]}
                            ]
                        }
                    }
                }
            ],
            "as": "recent_ratings"
        }
    })
    
    pipeline.append({
        "$match": {
            "$expr": {"$gt": [{"$size": "$recent_ratings"}, 0]}
        }
    })
    
    pipeline.append({
        "$addFields": {
            "trending_score": {
                "$multiply": [
                    {"$size": "$recent_ratings"},
                    {"$avg": "$recent_ratings.rating"}
                ]
            }
        }
    })
    
    pipeline.append({
        "$sort": {"trending_score": -1}
    })
    
    pipeline.append({
        "$limit": limit
    })
    
    pipeline.append({
        "$project": {
            "_id": 1,
            "item_type": 1,
            "title": 1,
            "name": 1,
            "description": 1,
            "genres": 1,
            "tags": 1,
            "metadata": 1,
            "created_at": 1,
            "updated_at": 1,
            "trending_score": 1
        }
    })
    
    items = await db.items.aggregate(pipeline).to_list(length=limit)
    
    result = []
    for item in items:
        item["id"] = str(item["_id"])
        item["recommendation_score"] = item.get("trending_score", 0)
        item["recommendation_type"] = "trending"
        result.append(item)
    
    return result

