from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserCredentials(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)


class User(BaseModel):
    id: Optional[str] = None
    username: str
    password: str
    first_name: str
    last_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
