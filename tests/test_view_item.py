"""GET /items/{id} and the carried C1 cleanup (view-item: B1-B7)."""

import ast
import threading
import time
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

import cart.errors
import cart.main
from cart.errors import ItemNotFoundError
from cart.models import Item
from cart.store import CartStore

NOT_FOUND_BODY = {"error": "not_found", "message": "Item does-not-exist not found"}


def create(client: TestClient) -> dict[str, Any]:
    response = client.post("/items", json={"name": "Coffee beans", "price": 8.5, "quantity": 2})
    assert response.status_code == 201
    body: dict[str, Any] = response.json()
    return body


def test_b1_ac_2_1_get_returns_the_created_item(client: TestClient) -> None:
    """B1 / AC-2.1 / DR-1: GET returns exactly the body the POST returned."""
    created = create(client)
    response = client.get(f"/items/{created['id']}")
    assert response.status_code == 200
    body = response.json()
    assert body == created
    assert set(body) == {"id", "name", "price", "quantity"}
    assert body["name"] == "Coffee beans"
    assert body["price"] == 8.5
    assert isinstance(body["price"], float)
    assert body["quantity"] == 2


def test_b2_ac_2_2_unknown_id_is_404_not_found(client: TestClient) -> None:
    """B2 / AC-2.2: 404 with the exact not_found body, id as sent."""
    response = client.get("/items/does-not-exist")
    assert response.status_code == 404
    assert response.json() == NOT_FOUND_BODY


def test_b3_ac_2_2_store_get_raises_for_unknown_id() -> None:
    """B3 / AC-2.2: CartStore.get raises ItemNotFoundError, never returns None."""
    store = CartStore()
    with pytest.raises(ItemNotFoundError) as info:
        store.get("x")
    assert info.value.item_id == "x"


def test_b4_ac_2_1_lookup_is_case_sensitive(client: TestClient) -> None:
    """B4 / AC-2.1: the upper-cased id of a uuid4 is not found."""
    created = create(client)
    response = client.get(f"/items/{created['id'].upper()}")
    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "not_found"
    assert body["message"] == f"Item {created['id'].upper()} not found"


def test_b5_ac_2_1_get_returns_added_item_and_leaves_cart_unchanged() -> None:
    """B5 / AC-2.1: get returns the item add returned; the cart is unchanged."""
    store = CartStore()
    added = store.add("Coffee beans", Decimal("8.5"), 2)
    before = store.list_all()
    fetched = store.get(added.id)
    assert isinstance(fetched, Item)
    assert fetched == added
    assert store.list_all() == before


def test_b5_ac_2_1_get_waits_for_the_store_lock() -> None:
    """B5 / AC-2.1: get takes store._lock, so it cannot finish while the lock is held."""
    store = CartStore()
    added = store.add("Coffee beans", Decimal("8.5"), 2)
    results: list[Item] = []

    def reader() -> None:
        results.append(store.get(added.id))

    store._lock.acquire()
    try:
        thread = threading.Thread(target=reader, daemon=True)
        thread.start()
        time.sleep(0.2)
        assert thread.is_alive()
        assert results == []
    finally:
        store._lock.release()
    thread.join(timeout=5)
    assert not thread.is_alive()
    assert results == [added]


@pytest.mark.parametrize(
    ("path", "message"),
    [
        ("/items/not-a-uuid", "Item not-a-uuid not found"),
        ("/items/%20", "Item   not found"),
    ],
)
def test_b6_ac_2_2_non_uuid_id_is_404_not_found(
    client: TestClient, path: str, message: str
) -> None:
    """B6 / AC-2.2: a non-UUID id answers 404 not_found, never 400 or 500."""
    response = client.get(path)
    assert response.status_code == 404
    assert response.json() == {"error": "not_found", "message": message}


def test_b7_c1_errors_module_has_no_assert_statement() -> None:
    """B7 / C1: errors.py narrows types without assert."""
    tree = ast.parse(Path(cart.errors.__file__).read_text())
    asserts = [node for node in ast.walk(tree) if isinstance(node, ast.Assert)]
    assert asserts == []


def test_b7_c1_invalid_post_body_still_400_validation_error(client: TestClient) -> None:
    """B7 / C1: the 400 validation_error answer is unchanged by the cleanup."""
    response = client.post("/items", json={"name": ""})
    assert response.status_code == 400
    assert response.json()["error"] == "validation_error"
