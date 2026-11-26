import re

from app.models import RiskSummary

# A number not glued to letters (skips "T019", "5Y"), with optional $, commas, decimals, K/M or %.
NUMBER = re.compile(r"(?<![\w.])-?\$?\d[\d,]*(?:\.\d+)?(?:[kKmM]|%)?(?!\w)")


def normalize(token: str) -> float | None:
    """'10.8K' -> 10800, '$1,234' -> 1234. Percentages return None: the backend never sends them."""
    t = token.replace("$", "").replace(",", "").lstrip("-")
    if t.endswith("%"):
        return None
    scale = {"k": 1_000, "m": 1_000_000}.get(t[-1].lower(), 1)
    if scale != 1:
        t = t[:-1]
    return float(t) * scale


def allowed_values(s: RiskSummary) -> set[float]:
    """Every number the backend sent to Claude."""
    vals = {s.total_dv01, s.limit, s.trade_count, s.over_by, s.headroom}
    if s.largest_trade:
        vals |= {s.largest_trade.dv01, s.largest_trade.notional}
    return {abs(round(v, 2)) for v in vals}


def find_unverified(text: str, summary: RiskSummary) -> list[str]:
    """Numbers in the text that the backend never sent (rounding to whole numbers allowed)."""
    allowed = allowed_values(summary)
    bad = []
    for token in NUMBER.findall(text):
        value = normalize(token)
        if value is None or not any(abs(value - a) <= 0.5 for a in allowed):
            bad.append(token)
    return bad
