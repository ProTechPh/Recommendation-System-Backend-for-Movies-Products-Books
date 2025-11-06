from typing import Optional
from pydantic import BaseModel
from app.models.item import ItemType


class RecommendationRequest(BaseModel):
    method: Optional[str] = "hybrid"
    limit: Optional[int] = 10
    item_type: Optional[ItemType] = None
    category: Optional[str] = None
    genre: Optional[str] = None


class RecommendationResponse(BaseModel):
    item_id: str
    item_type: str
    title: Optional[str] = None
    name: Optional[str] = None
    description: str
    recommendation_score: float
    recommendation_type: str
    genres: list = []
    tags: list = []
    metadata: dict = {}

