import pytest
from pydantic import ValidationError

from app.models import Trade
from app.risk_data import check_limits, dv01_by_book, generate_trades, largest_risk


def make_trade(trade_id: str, book: str, dv01: float) -> Trade:
    return Trade(trade_id=trade_id, book=book, instrument="X", notional=1_000_000, dv01=dv01)


def test_generate_trades_count():
    assert len(generate_trades(10)) == 10


def test_dv01_by_book_sums_per_book():
    trades = [
        make_trade("T001", "RATES", 100.0),
        make_trade("T002", "RATES", -40.0),
        make_trade("T003", "FX", 25.0),
    ]
    assert dv01_by_book(trades) == {"RATES": 60.0, "FX": 25.0}


def test_largest_risk_uses_absolute_value():
    trades = [make_trade("T001", "RATES", 100.0), make_trade("T002", "FX", -500.0)]
    assert largest_risk(trades).trade_id == "T002"


def test_check_limits_flags_breach():
    breaches = check_limits({"CREDIT": -7000.0}, {"CREDIT": 5000})
    assert breaches == [("CREDIT", -7000.0, 5000)]


def test_check_limits_no_breach():
    assert check_limits({"FX": 100.0}, {"FX": 8000}) == []


def test_invalid_book_rejected():
    with pytest.raises(ValidationError):
        make_trade("T001", "BANANA", 1.0)

def test_negative_notional_rejected():
    with pytest.raises(ValidationError):
        Trade(trade_id="T001", book="RATES", instrument="X", notional=-1_000_000, dv01=1.0)

def test_generate_trades_is_deterministic():
    import random

    random.seed(42)
    first = generate_trades(5)
    random.seed(42)
    second = generate_trades(5)
    assert first == second