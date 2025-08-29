from pydantic import BaseModel
from typing import List

class Source(BaseModel):
    tittle: str
    url: str

class ResearchResponse(BaseModel):
    question:str
    answer_summary: str
    source: List[Source]