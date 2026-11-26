"""Code computes, Claude explains, code checks: retry once, then fall back to a template."""
import logging
from collections.abc import Callable

from pydantic import ValidationError

from app import llm
from app.models import ExplanationOutput, RiskSummary
from app.validation import find_unverified

log = logging.getLogger("explainer")

RETRY_INSTRUCTION = (
    "Your previous answer was rejected because it contained figures that are not in "
    "<risk_summary>: {bad}. Use ONLY the figures in <risk_summary>, written exactly as given."
)


def fallback_text(s: RiskSummary) -> str:
    """Pre-built templates filled with verified numbers only."""
    if s.breach:
        return (f"{s.book} book DV01 is {s.total_dv01:,.2f}, which is {s.over_by:,.2f} "
                f"over its limit of {s.limit:,}.")
    return (f"{s.book} book DV01 is {s.total_dv01:,.2f}, within its limit of {s.limit:,}, "
            f"with {s.headroom:,.2f} of headroom.")


def explain_with_checks(
    summary: RiskSummary,
    call: Callable[..., ExplanationOutput] | None = None,
) -> tuple[ExplanationOutput, str]:
    """Returns (explanation, source) where source is 'claude', 'claude_retry' or 'fallback'."""
    call = call or llm.request_explanation
    extra = None
    for attempt, source in ((1, "claude"), (2, "claude_retry")):
        try:
            out = call(summary, extra)
        except (ValueError, ValidationError) as e:
            log.warning("book=%s attempt=%d invalid JSON: %s", summary.book, attempt, e)
            extra = "Your previous answer was not valid JSON. Respond with ONLY the JSON object."
            continue
        bad = find_unverified(" ".join([out.explanation, *out.key_drivers]), summary)
        if not bad:
            return out, source
        log.warning("book=%s attempt=%d unverified figures: %s", summary.book, attempt, bad)
        extra = RETRY_INSTRUCTION.format(bad=", ".join(bad))
    log.error("book=%s both attempts failed, using fallback", summary.book)
    return ExplanationOutput(explanation=fallback_text(summary)), "fallback"
