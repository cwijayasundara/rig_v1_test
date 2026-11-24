import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / ".rig/product/sprints/sprint-0/holdout"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from holdout_boot import fresh_client  # noqa: E402

def test_tc_20_unknown_id_is_404_not_found() -> None:
    client = fresh_client()
    r = client.get("/items/does-not-exist")
    assert r.status_code == 404
    assert r.json() == {"error": "not_found", "message": "Item does-not-exist not found"}
