from fastapi.testclient import TestClient

from cart.main import app

client = TestClient(app)


def test_smoke_empty_cart_lists_nothing() -> None:
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []
