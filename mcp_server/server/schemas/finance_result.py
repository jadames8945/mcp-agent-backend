from typing import Optional

from pydantic import BaseModel

class FundSummary(BaseModel):
    symbol: str
    name: str
    classification: Optional[str] = None
    expense_ratio: Optional[float] = None
    risk_level: Optional[int] = None
    url: Optional[str] = None
    total_assets: Optional[float] = None
    ytd_return: Optional[float] = None
    morningstar_rating: Optional[int] = None
    morningstar_risk: Optional[int] = None
    summary: Optional[str] = None

class FundSource(BaseModel):
    provider: str
    source_url: str

class FundDetails(BaseModel):
    summary: FundSummary
    source: FundSource