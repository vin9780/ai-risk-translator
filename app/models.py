from typing import Literal

from pydantic import BaseModel, Field

Book = Literal["RATES", "CREDIT", "FX"]


class Trade(BaseModel):
    trade_id: str = Field(pattern=r"^T\d{3}$")
    book: Book
    instrument: str
    notional: float = Field(gt=0)
    dv01: float

class RiskSummary(BaseModel):
    book: Book
    total_dv01: float
    trade_count: int
    largest_trade: Trade | None
    limit: int
    breach: bool
    over_by: float = 0.0     # how far over the limit (0 if within) - calculated by code
    headroom: float = 0.0    # room left before the limit (0 if breached) - calculated by code    

class ExplainRequest(BaseModel):
    book: Book

class ExplainResponse(BaseModel):
    book: Book
    summary: RiskSummary
    explanation: str    