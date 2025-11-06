from datetime import datetime
from pydantic import BaseModel, Field


class RatingSchema(BaseModel):
    id: str
    user_id: str
    item_id: str
    rating: int = Field(..., ge=1, le=5)
    created_at: datetime
    updated_at: datetime
