import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / ".rig/product/sprints/sprint-0/holdout"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from holdout_boot import fresh_client  # noqa: E402

def test_tc_18_missing_name_is_400_validation_error() -> None:
    client = fresh_client()
    r = client.post("/items", json={"price": 3, "quantity": 1})
    assert r.status_code == 400
    body = r.json()
    assert set(body) == {"error", "message"}
    assert body["error"] == "validation_error"
    assert isinstance(body["message"], str) and body["message"]
