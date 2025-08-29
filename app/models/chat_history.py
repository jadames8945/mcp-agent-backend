from datetime import datetime
from typing import List, Dict

from pydantic import BaseModel


class ChatHistory(BaseModel):
    email: str
    title: str
    chat_history: List[Dict[str, str]]
    created_at: datetime 