import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / ".rig/product/sprints/sprint-0/holdout"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from holdout_boot import fresh_client  # noqa: E402

def test_tc_19_view_item_happy_path() -> None:
    client = fresh_client()
    created = client.post("/items", json={"name": "Coffee beans", "price": 8.5, "quantity": 2}).json()
    r = client.get("/items/" + created["id"])
    assert r.status_code == 200
    assert r.json() == created
    assert r.json()["price"] == 8.5
    assert set(r.json()) == {"id", "name", "price", "quantity"}
