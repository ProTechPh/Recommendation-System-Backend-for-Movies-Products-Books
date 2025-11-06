from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    id: str
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime
    is_anonymous: bool = False
    preferences: Optional[dict] = None
