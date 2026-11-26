from anthropic import Anthropic
from dotenv import load_dotenv

from app.models import ExplanationOutput, RiskSummary

load_dotenv()
client = Anthropic()

SYSTEM_PROMPT = """You explain trading risk to non-technical stakeholders in plain English.
Rules:
- Use ONLY the numbers in the provided risk summary. Never calculate new figures.
- Explain what DV01 means for this book, whether it is within its limit, and what that implies.
- Answer in 3-4 sentences. No jargon without a short explanation."""


def explain_risk(summary: RiskSummary) -> str:
    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=300,
        thinking={"type": "disabled"},
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Explain this risk summary:\n{summary.model_dump_json(indent=2)}",
            }
        ],
    )
    return "".join(b.text for b in response.content if b.type == "text")

def stream_explanation(summary: RiskSummary):
    with client.messages.stream(
        model="claude-haiku-5-5",
        max_tokens=300,
        thinking={"type": "disabled"},
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Explain this risk summary:\n{summary.model_dump_json(indent=2)}",
            }
        ],
    ) as stream:
        for text in stream.text_stream:
            yield text
            

JSON_SYSTEM_PROMPT = """You explain trading risk to non-technical stakeholders in plain English.
Rules:
- Use ONLY the numbers inside <risk_summary>. Never calculate, round, abbreviate or spell out figures.
- Write every figure exactly as it appears in <risk_summary>.
- Say whether the book is within or over its limit, and name the largest trade if one is given.
- Respond with ONLY a JSON object, no other text:
  {"explanation": "<3-4 plain-English sentences>", "key_drivers": ["<short point>", "<short point>"]}"""


def request_explanation(summary: RiskSummary, extra_instruction: str | None = None) -> ExplanationOutput:
    """Ask Claude for a structured explanation. Raises ValueError/ValidationError if the JSON is bad."""
    content = f"<risk_summary>\n{summary.model_dump_json(indent=2)}\n</risk_summary>"
    if extra_instruction:
        content += f"\n\n{extra_instruction}"
    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=400,
        thinking={"type": "disabled"},
        system=JSON_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    )
    text = "".join(b.text for b in response.content if b.type == "text")
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object in Claude's response")
    return ExplanationOutput.model_validate_json(text[start : end + 1])
