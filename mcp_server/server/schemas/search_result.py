from typing import Optional

from pydantic import BaseModel


class SearchResultItem(BaseModel):
    url: str
    site_name: str
    query_answer: str


class SearchResponse(BaseModel):
    query_id: int
    query_text: str
    search_result: Optional[SearchResultItem] = None
    is_successful: bool
    searched_at: Optional[str] = None
    error_message: Optional[str] = None
