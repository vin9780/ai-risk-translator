from typing import Literal

from pydantic import BaseModel, Field

Book = Literal["RATES", "CREDIT", "FX"]


class Trade(BaseModel):
    trade_id: str = Field(pattern=r"^T\d{3}$")
    book: Book
    instrument: str
    notional: float = Field(gt=0)
    dv01: float