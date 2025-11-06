from typing import List, Dict, Optional
from collections import defaultdict
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.collaborative_filtering import generate_collaborative_recommendations
from app.services.content_based import generate_content_based_recommendations


async def generate_hybrid_recommendations(
    db: AsyncIOMotorDatabase,
    user_id: str,
    limit: int = 10,
    collaborative_weight: float = 0.6,
    content_weight: float = 0.4,
    min_similarity: float = 0.3
) -> List[Dict]:
    """Generate hybrid recommendations combining collaborative and content-based filtering"""
    
    collaborative_recs = await generate_collaborative_recommendations(
        db, user_id, limit=limit * 2, min_similarity=min_similarity
    )
    
    content_recs = await generate_content_based_recommendations(
        db, user_id, limit=limit * 2, min_similarity=min_similarity
    )
    
    def normalize_scores(recommendations: List[Dict]) -> List[Dict]:
        if not recommendations:
            return []
        
        max_score = max(rec.get("recommendation_score", 0) for rec in recommendations)
        if max_score == 0:
            return recommendations
        
        for rec in recommendations:
            rec["normalized_score"] = rec.get("recommendation_score", 0) / max_score
        
        return recommendations
    
    collaborative_recs = normalize_scores(collaborative_recs)
    content_recs = normalize_scores(content_recs)
    
    item_scores = defaultdict(lambda: {
        "item": None,
        "collaborative_score": 0.0,
        "content_score": 0.0,
        "hybrid_score": 0.0,
        "count": 0
    })
    
    for rec in collaborative_recs:
        item_id = rec.get("id")
        if item_id:
            item_scores[item_id]["item"] = rec
            item_scores[item_id]["collaborative_score"] = rec.get("normalized_score", 0)
            item_scores[item_id]["count"] += 1
    
    for rec in content_recs:
        item_id = rec.get("id")
        if item_id:
            if item_scores[item_id]["item"] is None:
                item_scores[item_id]["item"] = rec
            item_scores[item_id]["content_score"] = rec.get("normalized_score", 0)
            item_scores[item_id]["count"] += 1
    
    recommendations = []
    for item_id, data in item_scores.items():
        if data["item"] is None:
            continue
        
        hybrid_score = (
            collaborative_weight * data["collaborative_score"] +
            content_weight * data["content_score"]
        )
        
        if data["count"] > 1:
            hybrid_score *= 1.2
        
        item = data["item"].copy()
        item["recommendation_score"] = hybrid_score
        item["recommendation_type"] = "hybrid"
        item["collaborative_score"] = data["collaborative_score"]
        item["content_score"] = data["content_score"]
        
        recommendations.append(item)
    
    recommendations.sort(key=lambda x: x.get("recommendation_score", 0), reverse=True)
    
    return recommendations[:limit]


async def get_personalized_recommendations(
    db: AsyncIOMotorDatabase,
    user_id: str,
    limit: int = 10,
    method: str = "hybrid"
) -> List[Dict]:
    """Get personalized recommendations for a user"""
    
    if method == "collaborative":
        return await generate_collaborative_recommendations(db, user_id, limit=limit)
    elif method == "content":
        return await generate_content_based_recommendations(db, user_id, limit=limit)
    else:
        return await generate_hybrid_recommendations(db, user_id, limit=limit)

