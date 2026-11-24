import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / ".rig/product/sprints/sprint-0/holdout"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from holdout_boot import fresh_client  # noqa: E402

def test_tc_26_list_items_oldest_first() -> None:
    client = fresh_client()
    first = client.post("/items", json={"name": "Tea", "price": 3, "quantity": 1}).json()
    second = client.post("/items", json={"name": "Apples", "price": 1.25, "quantity": 6}).json()
    r = client.get("/items")
    assert r.status_code == 200
    assert r.json() == [first, second]
    for item in r.json():
        assert set(item) == {"id", "name", "price", "quantity"}
    assert [i["name"] for i in r.json()] == ["Tea", "Apples"]
