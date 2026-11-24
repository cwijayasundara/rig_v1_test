"""POST /items end to end (add-item: B1-B8, B12-B18)."""

import json
import uuid
from decimal import Decimal
from typing import Any

import pytest
from fastapi.testclient import TestClient

import cart.main

JSON = {"content-type": "application/json"}


def post_raw(client: TestClient, content: str) -> Any:
    return client.post("/items", content=content, headers=JSON)


def stored() -> list[Any]:
    items: list[Any] = cart.main.store.list_all()
    return items


def valid(**over: Any) -> dict[str, Any]:
    body: dict[str, Any] = {"name": "Tea", "price": 3, "quantity": 1}
    body.update(over)
    return body


def without(field: str) -> dict[str, Any]:
    body = valid()
    del body[field]
    return body


def test_b1_ac_1_1_adds_item_and_returns_201(client: TestClient) -> None:
    """B1 / AC-1.1 / DR-1: exact response shape."""
    response = client.post("/items", json={"name": "Coffee beans", "price": 8.5, "quantity": 2})
    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "name", "price", "quantity"}
    assert isinstance(body["id"], str)
    assert body["name"] == "Coffee beans"
    assert body["price"] == 8.5
    assert isinstance(body["price"], float)
    assert body["quantity"] == 2
    assert isinstance(body["quantity"], int)


def test_b2_ac_1_1_added_item_is_stored(client: TestClient) -> None:
    """B2 / AC-1.1: list_all holds the item after the 201."""
    body = client.post("/items", json={"name": "Coffee beans", "price": 8.5, "quantity": 2}).json()
    items = stored()
    assert len(items) == 1
    assert items[0].id == body["id"]
    assert items[0].name == "Coffee beans"
    assert items[0].price == Decimal("8.5")
    assert items[0].quantity == 2


def test_b3_ac_1_2_identical_adds_get_different_ids(client: TestClient) -> None:
    """B3 / AC-1.2: both kept, different ids."""
    first = client.post("/items", json=valid())
    second = client.post("/items", json=valid())
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] != second.json()["id"]
    assert len(stored()) == 2


def test_b4_response_id_is_uuid4(client: TestClient) -> None:
    """B4 / DR-2: the id in the response is a canonical uuid4."""
    item_id = client.post("/items", json=valid()).json()["id"]
    parsed = uuid.UUID(item_id)
    assert parsed.version == 4
    assert str(parsed) == item_id


def test_b5_name_is_trimmed(client: TestClient) -> None:
    """B5 / DR-3: leading and trailing whitespace is trimmed."""
    response = client.post("/items", json=valid(name="  Coffee beans "))
    assert response.status_code == 201
    assert response.json()["name"] == "Coffee beans"
    assert stored()[0].name == "Coffee beans"


def test_b5_inner_whitespace_is_kept(client: TestClient) -> None:
    """B5 / DR-3: stored exactly as sent apart from the ends."""
    response = client.post("/items", json=valid(name=" Green  tea\t"))
    assert response.json()["name"] == "Green  tea"


@pytest.mark.parametrize(
    ("price", "expected"),
    [(0, 0), (8.99, 8.99), (8.5, 8.5), (3, 3), (0.01, 0.01), (12.34, 12.34)],
)
def test_b6_dr_4_price_is_returned_as_json_number(
    client: TestClient, price: float, expected: float
) -> None:
    """B6 / DR-4: 0 and 2-decimal prices accepted, returned as numbers."""
    response = client.post("/items", json=valid(price=price))
    assert response.status_code == 201
    assert response.json()["price"] == expected
    assert not isinstance(response.json()["price"], str)


def test_b6_dr_4_price_8_5_is_not_rendered_as_string(client: TestClient) -> None:
    """B6 / DR-4: 8.5 not "8.50"."""
    response = post_raw(client, '{"name":"Tea","price":8.50,"quantity":1}')
    assert response.status_code == 201
    assert response.json()["price"] == 8.5
    assert not isinstance(response.json()["price"], str)
    stored_price = stored()[0].price
    assert isinstance(stored_price, Decimal)
    assert stored_price == Decimal("8.5")


@pytest.mark.parametrize("quantity", [1, 2, 1000000000000])
def test_b7_dr_5_quantity_accepted_without_upper_limit(client: TestClient, quantity: int) -> None:
    """B7 / DR-5: 1 is the minimum, no upper limit."""
    response = client.post("/items", json=valid(quantity=quantity))
    assert response.status_code == 201
    assert response.json()["quantity"] == quantity


def test_b8_ac_1_7_extra_fields_are_ignored(client: TestClient) -> None:
    """B8 / AC-1.7: unknown fields do not appear and do not fail."""
    response = client.post("/items", json=valid(colour="red", extra=[1, 2]))
    assert response.status_code == 201
    assert set(response.json()) == {"id", "name", "price", "quantity"}
    assert len(stored()) == 1


def test_b8_ac_1_7_client_id_is_ignored(client: TestClient) -> None:
    """B8 / AC-1.7 / DR-2: the server generates the id itself."""
    response = client.post("/items", json=valid(id="my-own-id"))
    assert response.status_code == 201
    new_id = response.json()["id"]
    assert new_id != "my-own-id"
    assert uuid.UUID(new_id).version == 4
    assert stored()[0].id == new_id


def assert_rejected(response: Any, field: str) -> None:
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "validation_error"
    assert field in body["message"]
    assert stored() == []


@pytest.mark.parametrize("name", [5, None, "", "   ", "\t\n", True, ["Tea"]], ids=repr)
def test_b12_ac_1_3_bad_name_is_rejected(client: TestClient, name: Any) -> None:
    """B12 / AC-1.3: not a string, empty or whitespace only."""
    assert_rejected(client.post("/items", json=valid(name=name)), "name")


def test_b12_ac_1_3_missing_name_is_rejected(client: TestClient) -> None:
    """B12 / AC-1.3: missing name."""
    assert_rejected(client.post("/items", json=without("name")), "name")


@pytest.mark.parametrize(
    "price", ["8.50", None, True, False, -0.01, 8.505, -1, 1.001, []], ids=repr
)
def test_b13_ac_1_4_bad_price_is_rejected(client: TestClient, price: Any) -> None:
    """B13 / AC-1.4: not a number, negative or more than 2 decimals."""
    assert_rejected(client.post("/items", json=valid(price=price)), "price")


def test_b13_ac_1_4_missing_price_is_rejected(client: TestClient) -> None:
    """B13 / AC-1.4: missing price."""
    assert_rejected(client.post("/items", json=without("price")), "price")


@pytest.mark.parametrize("token", ["NaN", "Infinity", "-Infinity"])
def test_b13_ac_1_4_non_finite_price_is_rejected(client: TestClient, token: str) -> None:
    """B13 / AC-1.4: NaN and Infinity sent as raw content are rejected."""
    response = post_raw(client, '{"name": "Tea", "price": ' + token + ', "quantity": 1}')
    assert_rejected(response, "price")


@pytest.mark.parametrize("quantity", [8.0, "2", True, False, 0, -1, None, 1.5], ids=repr)
def test_b14_ac_1_5_bad_quantity_is_rejected(client: TestClient, quantity: Any) -> None:
    """B14 / AC-1.5: not an integer or below 1."""
    assert_rejected(client.post("/items", json=valid(quantity=quantity)), "quantity")


def test_b14_ac_1_5_missing_quantity_is_rejected(client: TestClient) -> None:
    """B14 / AC-1.5: missing quantity."""
    assert_rejected(client.post("/items", json=without("quantity")), "quantity")


@pytest.mark.parametrize(
    "content",
    ["{not json", "", "[]", '"x"', "5", "null", '{"name": "Tea",', "[1, 2]"],
    ids=repr,
)
def test_b15_ac_1_6_bad_body_is_rejected(client: TestClient, content: str) -> None:
    """B15 / AC-1.6: invalid JSON, empty or non-object body names body."""
    assert_rejected(post_raw(client, content), "body")


def test_b15_ac_1_6_request_without_body(client: TestClient) -> None:
    """B15 / AC-1.6: a POST with no body at all names body."""
    assert_rejected(client.post("/items"), "body")


def test_b16_ac_1_8_exact_message(client: TestClient) -> None:
    """B16 / AC-1.8: the spec's example message, exactly."""
    response = client.post("/items", json={"name": "Tea", "price": 3, "quantity": 0})
    assert response.status_code == 400
    assert response.json() == {
        "error": "validation_error",
        "message": "quantity must be an integer of at least 1",
    }


@pytest.mark.parametrize(
    ("body", "field"),
    [
        (valid(name=""), "name"),
        (valid(price=-1), "price"),
        (valid(quantity=0), "quantity"),
    ],
    ids=["name", "price", "quantity"],
)
def test_b16_ac_1_8_message_follows_field_must_be_form(
    client: TestClient, body: dict[str, Any], field: str
) -> None:
    """B16 / AC-1.8: '<field> must be ...'."""
    response = client.post("/items", json=body)
    assert response.status_code == 400
    assert response.json()["message"].startswith(field + " must be ")


@pytest.mark.parametrize(
    ("body", "field"),
    [
        ({"name": "", "price": -1, "quantity": 0}, "name"),
        ({"name": 5, "price": "x", "quantity": "y"}, "name"),
        ({"price": -1, "quantity": 0}, "name"),
        ({"name": "Tea", "price": -1, "quantity": 0}, "price"),
        ({"name": "Tea", "quantity": 0}, "price"),
        ({"name": "Tea", "price": 3, "quantity": 0}, "quantity"),
    ],
    ids=["all-bad", "all-wrong-type", "name-missing", "price-first", "price-missing", "qty-only"],
)
def test_b17_ac_1_8_first_invalid_field_is_named(
    client: TestClient, body: dict[str, Any], field: str
) -> None:
    """B17 / AC-1.8: order name, price, quantity; one 400 body."""
    response = client.post("/items", json=body)
    assert response.status_code == 400
    message = response.json()["message"]
    assert message.startswith(field + " must be ")
    assert stored() == []


@pytest.mark.parametrize(
    "content",
    [
        json.dumps({"name": "", "price": 3, "quantity": 1}),
        json.dumps({"name": "Tea", "price": "x", "quantity": 1}),
        json.dumps({"name": "Tea", "price": 3, "quantity": 0}),
        "{broken",
        "[]",
        "",
    ],
    ids=["name", "price", "quantity", "invalid-json", "array", "empty"],
)
def test_b18_ac_1_3_failures_are_400_never_422(client: TestClient, content: str) -> None:
    """B18 / AC-1.3: 400 with exactly error and message keys."""
    response = post_raw(client, content)
    assert response.status_code == 400
    body = response.json()
    assert set(body) == {"error", "message"}
    assert body["error"] == "validation_error"
    assert isinstance(body["message"], str)
    assert body["message"] != ""
