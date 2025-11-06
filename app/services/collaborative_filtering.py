from typing import List, Dict, Tuple
from collections import defaultdict
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import math


async def get_user_ratings_dict(
    db: AsyncIOMotorDatabase,
    user_id: str
) -> Dict[str, float]:
    """Get all ratings for a user as a dictionary {item_id: rating}"""
    cursor = db.ratings.find({"user_id": user_id})
    ratings = await cursor.to_list(length=None)
    
    return {rating["item_id"]: float(rating["rating"]) for rating in ratings}


async def get_all_users_ratings(
    db: AsyncIOMotorDatabase
) -> Dict[str, Dict[str, float]]:
    """Get all user ratings as {user_id: {item_id: rating}}"""
    cursor = db.ratings.find({})
    ratings = await cursor.to_list(length=None)
    
    user_ratings = defaultdict(dict)
    for rating in ratings:
        user_id = rating["user_id"]
        item_id = rating["item_id"]
        user_ratings[user_id][item_id] = float(rating["rating"])
    
    return dict(user_ratings)


def cosine_similarity(
    ratings1: Dict[str, float],
    ratings2: Dict[str, float]
) -> float:
    """Calculate cosine similarity between two users' ratings"""
    common_items = set(ratings1.keys()) & set(ratings2.keys())
    
    if len(common_items) == 0:
        return 0.0
    
    dot_product = sum(ratings1[item] * ratings2[item] for item in common_items)
    magnitude1 = math.sqrt(sum(ratings1[item] ** 2 for item in common_items))
    magnitude2 = math.sqrt(sum(ratings2[item] ** 2 for item in common_items))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def pearson_correlation(
    ratings1: Dict[str, float],
    ratings2: Dict[str, float]
) -> float:
    """Calculate Pearson correlation coefficient between two users' ratings"""
    common_items = list(set(ratings1.keys()) & set(ratings2.keys()))
    
    if len(common_items) < 2:
        return 0.0
    
    mean1 = sum(ratings1[item] for item in common_items) / len(common_items)
    mean2 = sum(ratings2[item] for item in common_items) / len(common_items)
    
    numerator = sum(
        (ratings1[item] - mean1) * (ratings2[item] - mean2)
        for item in common_items
    )
    
    sum_sq_diff1 = sum((ratings1[item] - mean1) ** 2 for item in common_items)
    sum_sq_diff2 = sum((ratings2[item] - mean2) ** 2 for item in common_items)
    
    denominator = math.sqrt(sum_sq_diff1 * sum_sq_diff2)
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator


async def find_similar_users(
    db: AsyncIOMotorDatabase,
    user_id: str,
    min_common_items: int = 3,
    top_n: int = 10
) -> List[Tuple[str, float]]:
    """Find users similar to the given user"""
    user_ratings = await get_user_ratings_dict(db, user_id)
    
    if len(user_ratings) == 0:
        return []
    
    all_users_ratings = await get_all_users_ratings(db)
    similarities = []
    
    for other_user_id, other_ratings in all_users_ratings.items():
        if other_user_id == user_id:
            continue
        
        common_items = set(user_ratings.keys()) & set(other_ratings.keys())
        if len(common_items) < min_common_items:
            continue
        
        similarity = pearson_correlation(user_ratings, other_ratings)
        
        if similarity > 0:
            similarities.append((other_user_id, similarity))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]


async def generate_collaborative_recommendations(
    db: AsyncIOMotorDatabase,
    user_id: str,
    limit: int = 10,
    min_similarity: float = 0.3
) -> List[Dict]:
    """Generate recommendations using collaborative filtering"""
    user_ratings = await get_user_ratings_dict(db, user_id)
    user_rated_items = set(user_ratings.keys())
    
    similar_users = await find_similar_users(
        db, user_id, min_common_items=3, top_n=50
    )
    
    if len(similar_users) == 0:
        return []
    
    item_scores = defaultdict(lambda: {"score": 0.0, "count": 0})
    
    for similar_user_id, similarity in similar_users:
        if similarity < min_similarity:
            continue
        
        similar_user_ratings = await get_user_ratings_dict(db, similar_user_id)
        
        for item_id, rating in similar_user_ratings.items():
            if item_id not in user_rated_items:
                item_scores[item_id]["score"] += similarity * rating
                item_scores[item_id]["count"] += 1
    
    recommendations = []
    for item_id, data in item_scores.items():
        if data["count"] > 0:
            avg_score = data["score"] / data["count"]
            recommendations.append({
                "item_id": item_id,
                "score": avg_score,
                "similarity_count": data["count"]
            })
    
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    
    result = []
    for rec in recommendations[:limit]:
        item = await db.items.find_one({"_id": ObjectId(rec["item_id"])})
        if item:
            item["id"] = str(item["_id"])
            item["recommendation_score"] = rec["score"]
            item["recommendation_type"] = "collaborative"
            result.append(item)
    
    return result
