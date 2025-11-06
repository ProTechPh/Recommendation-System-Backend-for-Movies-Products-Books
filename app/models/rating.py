from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RatingBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")


class RatingCreate(RatingBase):
    item_id: str


class RatingUpdate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")


class Rating(RatingBase):
    id: str
    user_id: str
    item_id: str
    created_at: datetime
    updated_at: datetime


class RatingInDB(Rating):
    pass


class UserRating(Rating):
    item_title: Optional[str] = None
    item_name: Optional[str] = None


class ItemRating(Rating):
    username: Optional[str] = None
