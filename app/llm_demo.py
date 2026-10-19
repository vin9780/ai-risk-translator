from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=250,
    thinking={"type": "disabled"},
    system="You explain trading risk to non-technical stakeholders in plain English. Answer in 2-3 sentences.",
    messages=[
        {"role": "user", "content": "Our CREDIT book has a DV01 of -7,947 against a limit of 5,000. What does that mean?"}
    ],
)

text = "".join(block.text for block in response.content if block.type == "text")
print(text)
print("\n---")
print([block.type for block in response.content])
print(f"Stop reason: {response.stop_reason}")
print(f"Input tokens: {response.usage.input_tokens}, output tokens: {response.usage.output_tokens}")