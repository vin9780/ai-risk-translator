import random

class Trade:
    def __init__(self, trade_id, book, instrument, notional, dv01):
        self.trade_id = trade_id
        self.book = book
        self.instrument = instrument
        self.notional = notional
        self.dv01 = dv01

    def __repr__(self):
        return f"Trade({self.trade_id}, {self.book}, {self.instrument}, dv01={self.dv01:,.2f})"

BOOKS = ["RATES", "CREDIT", "FX"]

INSTRUMENTS = {
    "RATES": ["2Y Swap", "5Y Swap", "10Y Bond"],
    "CREDIT": ["IG CDS", "HY Bond", "Corp Bond"],
    "FX": ["USD/CAD Fwd", "EUR/USD Swap", "GBP/USD Fwd"],
}

LIMITS = {"RATES": 10_000, "CREDIT": 5_000, "FX": 8_000}


def generate_trades(n):
    trades = []
    for i in range(1, n+1):
        book = random.choice(BOOKS)
        trade = Trade(
            trade_id=f"T{i:03d}",
            book=book,
            instrument=random.choice(INSTRUMENTS[book]),
            notional=round(random.uniform(1_000_000, 50_000_000), 2),
            dv01=round(random.uniform(-5000, 5000), 2),
        )
        trades.append(trade)
    return trades

def dv01_by_book(trades):
    totals = {}
    for t in trades:
        totals[t.book] = totals.get(t.book, 0) + t.dv01
    return totals


def largest_risk(trades):
    return max(trades, key=lambda t: abs(t.dv01))

def check_limits(totals, limits):
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