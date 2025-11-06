from typing import List, Dict
from collections import Counter
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import math


def extract_item_features(item: dict) -> Dict[str, float]:
    """Extract features from an item for similarity calculation"""
    features = {}
    
    for genre in item.get("genres", []):
        features[f"genre:{genre}"] = 1.0
    
    for tag in item.get("tags", []):
        features[f"tag:{tag}"] = 1.0
    
    features[f"type:{item.get('item_type', '')}"] = 1.0
    
    metadata = item.get("metadata", {})
    
    if item.get("item_type") == "movie":
        if metadata.get("director"):
            features[f"director:{metadata['director']}"] = 1.0
        if metadata.get("cast"):
            for actor in metadata["cast"][:5]:
                features[f"actor:{actor}"] = 0.5
    
    if item.get("item_type") == "product":
        if metadata.get("brand"):
            features[f"brand:{metadata['brand']}"] = 1.0
        if item.get("category"):
            features[f"category:{item['category']}"] = 1.0
    
    if item.get("item_type") == "book":
        if metadata.get("author"):
            features[f"author:{metadata['author']}"] = 1.0
        if metadata.get("publisher"):
            features[f"publisher:{metadata['publisher']}"] = 0.5
    
    return features


def cosine_similarity_features(
    features1: Dict[str, float],
    features2: Dict[str, float]
) -> float:
    """Calculate cosine similarity between two feature vectors"""
    all_features = set(features1.keys()) | set(features2.keys())
    
    if len(all_features) == 0:
        return 0.0
    
    dot_product = sum(
        features1.get(f, 0.0) * features2.get(f, 0.0)
        for f in all_features
    )
    
    magnitude1 = math.sqrt(sum(features1.get(f, 0.0) ** 2 for f in all_features))
    magnitude2 = math.sqrt(sum(features2.get(f, 0.0) ** 2 for f in all_features))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def jaccard_similarity(
    set1: set,
    set2: set
) -> float:
    """Calculate Jaccard similarity between two sets"""
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    if union == 0:
        return 0.0
    
    return intersection / union


async def get_user_preferred_features(
    db: AsyncIOMotorDatabase,
    user_id: str,
    min_rating: float = 3.0
) -> Dict[str, float]:
    """Extract preferred features from user's rated items"""
    cursor = db.ratings.find({"user_id": user_id})
    ratings = await cursor.to_list(length=None)
    
    if len(ratings) == 0:
        return {}
    
    item_ids = [
        ObjectId(rating["item_id"])
        for rating in ratings
        if rating["rating"] >= min_rating
    ]
    
    if len(item_ids) == 0:
        return {}
    
    items = await db.items.find({"_id": {"$in": item_ids}}).to_list(length=None)
    
    feature_weights = Counter()
    
    for rating in ratings:
        if rating["rating"] < min_rating:
            continue
        
        item_id = ObjectId(rating["item_id"])
        item = next((i for i in items if i["_id"] == item_id), None)
        
        if item:
            item_features = extract_item_features(item)
            rating_weight = rating["rating"] / 5.0
            
            for feature, value in item_features.items():
                feature_weights[feature] += value * rating_weight
    
    if len(feature_weights) == 0:
        return {}
    
    max_weight = max(feature_weights.values())
    if max_weight > 0:
        return {feature: weight / max_weight for feature, weight in feature_weights.items()}
    
    return dict(feature_weights)


async def find_similar_items(
    db: AsyncIOMotorDatabase,
    item_id: str,
    limit: int = 10,
    min_similarity: float = 0.3
) -> List[Dict]:
    """Find items similar to the given item"""
    if not ObjectId.is_valid(item_id):
        return []
    
    item = await db.items.find_one({"_id": ObjectId(item_id)})
    if not item:
        return []
    
    item_features = extract_item_features(item)
    item_type = item.get("item_type")
    
    cursor = db.items.find({
        "item_type": item_type,
        "_id": {"$ne": ObjectId(item_id)}
    })
    all_items = await cursor.to_list(length=None)
    
    similarities = []
    
    for other_item in all_items:
        other_features = extract_item_features(other_item)
        similarity = cosine_similarity_features(item_features, other_features)
        
        if similarity >= min_similarity:
            other_item["id"] = str(other_item["_id"])
            other_item["similarity_score"] = similarity
            similarities.append((other_item, similarity))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    result = []
    for item_dict, similarity in similarities[:limit]:
        item_dict["recommendation_score"] = similarity
        item_dict["recommendation_type"] = "content_based"
        result.append(item_dict)
    
    return result


async def generate_content_based_recommendations(
    db: AsyncIOMotorDatabase,
    user_id: str,
    limit: int = 10,
    min_similarity: float = 0.3
) -> List[Dict]:
    """Generate recommendations using content-based filtering"""
    user_features = await get_user_preferred_features(db, user_id, min_rating=3.0)
    
    if len(user_features) == 0:
        return []
    
    cursor = db.ratings.find({"user_id": user_id})
    user_ratings = await cursor.to_list(length=None)
    user_rated_item_ids = {ObjectId(rating["item_id"]) for rating in user_ratings}
    
    cursor = db.items.find({})
    all_items = await cursor.to_list(length=None)
    
    similarities = []
    
    for item in all_items:
        item_id = item["_id"]
        
        if item_id in user_rated_item_ids:
            continue
        
        item_features = extract_item_features(item)
        similarity = cosine_similarity_features(user_features, item_features)
        
        if similarity >= min_similarity:
            item["id"] = str(item["_id"])
            item["recommendation_score"] = similarity
            item["recommendation_type"] = "content_based"
            similarities.append((item, similarity))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return [item for item, _ in similarities[:limit]]
