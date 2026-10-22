from anthropic import Anthropic
from dotenv import load_dotenv

from app.models import RiskSummary

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
            