from app.explainer import explain_with_checks, fallback_text
from app.models import ExplanationOutput, RiskSummary

BREACH = RiskSummary(book="RATES", total_dv01=-10800.0, trade_count=7, largest_trade=None,
                     limit=10000, breach=True, over_by=800.0, headroom=0.0)
WITHIN = RiskSummary(book="RATES", total_dv01=-8500.0, trade_count=6, largest_trade=None,
                     limit=10000, breach=False, over_by=0.0, headroom=1500.0)

GOOD = ExplanationOutput(explanation="RATES DV01 is -10,800, 800 over its limit of 10,000.")
BAD = ExplanationOutput(explanation="RATES is 8% over its limit.")


def fake(*answers):
    """A fake Claude that returns the given answers in order (an Exception is raised)."""
    calls = []

    def call(summary, extra=None):
        calls.append(extra)
        a = answers[len(calls) - 1]
        if isinstance(a, Exception):
            raise a
        return a

    call.calls = calls
    return call


def test_scenario_1_correct_first_time():
    out, source = explain_with_checks(BREACH, fake(GOOD))
    assert source == "claude" and out == GOOD


def test_scenario_2_fixed_on_retry():
    call = fake(BAD, GOOD)
    out, source = explain_with_checks(BREACH, call)
    assert source == "claude_retry" and out == GOOD
    assert "8%" in call.calls[1]          # retry tells Claude which figure was wrong


def test_scenario_3_fallback_after_two_failures():
    out, source = explain_with_checks(BREACH, fake(BAD, BAD))
    assert source == "fallback"
    assert out.explanation == "RATES book DV01 is -10,800.00, which is 800.00 over its limit of 10,000."


def test_invalid_json_then_good():
    out, source = explain_with_checks(BREACH, fake(ValueError("no JSON"), GOOD))
    assert source == "claude_retry"


def test_within_limit_fallback_template():
    assert fallback_text(WITHIN) == ("RATES book DV01 is -8,500.00, within its limit of 10,000, "
                                     "with 1,500.00 of headroom.")
