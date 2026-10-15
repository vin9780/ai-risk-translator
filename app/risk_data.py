import random

from app.models import Trade

BOOKS = ["RATES", "CREDIT", "FX"]

INSTRUMENTS = {
    "RATES": ["2Y Swap", "5Y Swap", "10Y Bond"],
    "CREDIT": ["IG CDS", "HY Bond", "Corp Bond"],
    "FX": ["USD/CAD Fwd", "EUR/USD Swap", "GBP/USD Fwd"],
}

LIMITS = {"RATES": 10_000, "CREDIT": 5_000, "FX": 8_000}


def generate_trades(n: int) -> list[Trade]:
    trades = []
    for i in range(1, n + 1):
        book = random.choice(BOOKS)
        trades.append(
            Trade(
                trade_id=f"T{i:03d}",
                book=book,
                instrument=random.choice(INSTRUMENTS[book]),
                notional=round(random.uniform(1_000_000, 50_000_000), 2),
                dv01=round(random.uniform(-5000, 5000), 2),
            )
        )
    return trades


def dv01_by_book(trades: list[Trade]) -> dict[str, float]:
    totals: dict[str, float] = {}
    for t in trades:
        totals[t.book] = totals.get(t.book, 0) + t.dv01
    return totals


def largest_risk(trades: list[Trade]) -> Trade:
    return max(trades, key=lambda t: abs(t.dv01))


def check_limits(
    totals: dict[str, float], limits: dict[str, int]
) -> list[tuple[str, float, int]]:
    breaches = []
    for book, total in totals.items():
        limit = limits.get(book)
        if limit is not None and abs(total) > limit:
            breaches.append((book, total, limit))
    return breaches


if __name__ == "__main__":
    random.seed(42)
    trades = generate_trades(20)

    totals = dv01_by_book(trades)
    print("DV01 by book:")
    for book, total in totals.items():
        print(f"  {book}: {total:,.2f}")

    print(f"\nLargest risk: {largest_risk(trades)}")

    breaches = check_limits(totals, LIMITS)
    if breaches:
        print("\nLimit breaches:")
        for book, total, limit in breaches:
            print(f"  {book}: {total:,.2f} exceeds limit {limit:,}")
    else:
        print("\nNo limit breaches")