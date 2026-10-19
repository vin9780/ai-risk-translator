# AI Risk Translator

An LLM-powered platform that translates trading risk metrics (DV01, cashflows) into plain-language explanations for non-technical stakeholders. All data is synthetic.

## Tech stack
- **Backend:** Python, FastAPI, Pydantic
- **LLM:** Claude Sonnet / Haiku (coming in Week 2)
- **Frontend:** React (coming in Week 2)
- **Testing:** pytest

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs for the interactive API docs.

## Run tests
```bash
python -m pytest -v
```

## Endpoints
| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/trades` | List trades, filter by `book`, `limit` |
| GET | `/trades/{trade_id}` | Get one trade |
| POST | `/trades` | Add a trade (validated) |
| GET | `/risk/{book}` | DV01 total, largest trade, limit breach for a book |

## Roadmap
- [x] Week 1: Synthetic risk data, FastAPI, tests
- [ ] Week 2-3: Claude API explanations, streaming, structured output
- [ ] Week 4: Tool use for deterministic risk calculations
- [ ] Week 5-6: RAG over risk policy documents (pgvector)
- [ ] Week 7-8: Agent for day-over-day risk changes, MCP server
- [ ] Week 9: Evaluation suite
- [ ] Week 10-11: Docker, AWS deployment, observability