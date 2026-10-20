import random

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.llm import explain_risk
from app.models import Book, ExplainRequest, ExplainResponse, RiskSummary, Trade
from app.risk_data import LIMITS, generate_trades, largest_risk

app = FastAPI(title="AI Risk Translator")

random.seed(42)
TRADES: list[Trade] = generate_trades(20)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


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


def build_risk_summary(book: Book) -> RiskSummary:
    trades = [t for t in TRADES if t.book == book]
    total = round(sum(t.dv01 for t in trades), 2)
    limit = LIMITS[book]
    return RiskSummary(
        book=book,
        total_dv01=total,
        trade_count=len(trades),
        largest_trade=largest_risk(trades) if trades else None,
        limit=limit,
        breach=abs(total) > limit,
    )


@app.get("/risk/{book}", response_model=RiskSummary)
def get_book_risk(book: Book):
    return build_risk_summary(book)


@app.post("/explain", response_model=ExplainResponse)
def explain(request: ExplainRequest):
    summary = build_risk_summary(request.book)
    explanation = explain_risk(summary)
    return ExplainResponse(book=request.book, summary=summary, explanation=explanation)