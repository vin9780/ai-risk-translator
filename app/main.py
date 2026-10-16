import random

from fastapi import FastAPI, HTTPException, Query

from app.models import Book, Trade
from app.risk_data import generate_trades

app = FastAPI(title="AI Risk Translator")

random.seed(42)
TRADES: list[Trade] = generate_trades(20)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/trades", response_model=list[Trade])
def list_trades(book: Book | None = None, limit: int = Query(10, ge=1, le=100)):
    trades = [t for t in TRADES if book is None or t.book == book]
    return trades[:limit]


@app.get("/trades/{trade_id}", response_model=Trade)
def get_trade(trade_id: str):
    for t in TRADES:
        if t.trade_id == trade_id:
            return t
    raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")


@app.post("/trades", response_model=Trade, status_code=201)
def add_trade(trade: Trade):
    TRADES.append(trade)
    return trade