from app.models import RiskSummary, Trade
from app.validation import find_unverified

SUMMARY = RiskSummary(
    book="RATES", total_dv01=-10800.0, trade_count=7, limit=10000,
    breach=True, over_by=800.0, headroom=0.0,
    largest_trade=Trade(trade_id="T021", book="RATES", instrument="10Y Swap",
                        notional=25_000_000, dv01=-2300.0),
)


def test_exact_numbers_pass():
    text = "RATES DV01 is -10,800, which is 800 over its limit of 10,000, driven by T021 (DV01 -2,300)."
    assert find_unverified(text, SUMMARY) == []


def test_invented_percentage_is_caught():
    assert find_unverified("The book is 8% over its limit.", SUMMARY) == ["8%"]


def test_k_suffix_is_normalized():
    assert find_unverified("DV01 is about 10.8K.", SUMMARY) == []


def test_invented_number_is_caught():
    assert find_unverified("It would lose $1,080,000 if rates rose 1%.", SUMMARY) == ["$1,080,000", "1%"]


def test_trade_ids_and_tenors_are_ignored():
    assert find_unverified("Trade T021 is a 10Y Swap.", SUMMARY) == []
