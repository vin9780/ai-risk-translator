from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_trades_default_limit():
    response = client.get("/trades")
    assert response.status_code == 200
    assert len(response.json()) == 10


def test_filter_by_book():
    response = client.get("/trades", params={"book": "CREDIT"})
    assert all(t["book"] == "CREDIT" for t in response.json())


def test_unknown_trade_returns_404():
    response = client.get("/trades/T999")
    assert response.status_code == 404

def test_limit_over_100_rejected():
    response = client.get("/trades",params={"limit": 101})
    assert response.status_code == 422

def test_negative_notional_rejected_by_api():
    trade_data = {
        "trade_id": "T999",
        "book": "RATES",
        "instrument": "X",
        "notional": -5,
        "dv01": 1.0
    }
    response = client.post("/trades", json=trade_data)
    assert response.status_code == 422        