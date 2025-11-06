from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.item import ItemType


class ItemSchema(BaseModel):
    id: str
    item_type: ItemType
    title: Optional[str] = None
    name: Optional[str] = None
    description: str
    genres: List[str]
    tags: List[str]
    metadata: dict
    created_at: datetime
    updated_at: datetime
