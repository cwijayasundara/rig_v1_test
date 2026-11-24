import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / ".rig/product/sprints/sprint-0/holdout"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from holdout_boot import fresh_client  # noqa: E402

def test_tc_1_add_item_happy_path() -> None:
    client = fresh_client()
    r = client.post("/items", json={"name": "Coffee beans", "price": 8.5, "quantity": 2})
    assert r.status_code == 201
    body = r.json()
    assert set(body) == {"id", "name", "price", "quantity"}
    assert isinstance(body["id"], str) and body["id"]
    assert body["name"] == "Coffee beans"
    assert body["price"] == 8.5 and not isinstance(body["price"], str)
    assert body["quantity"] == 2 and isinstance(body["quantity"], int)
