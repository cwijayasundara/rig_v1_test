"""POST /items end to end (add-item: B1-B8, B12-B18)."""

import json
import uuid
from decimal import Decimal
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import cart.main
from cart.store import CartStore

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


MSG_NAME = "name must be a non-empty string"
MSG_PRICE = "price must be a number of at least 0 with at most 2 decimal places"
MSG_QUANTITY = "quantity must be an integer of at least 1"
MSG_BODY = "body must be a JSON object"


def assert_exact(response: Any, message: str) -> None:
    assert response.status_code == 400
    assert response.json() == {"error": "validation_error", "message": message}
    assert stored() == []


@pytest.mark.parametrize(
    "content",
    ["{not json", "", "[]", '"x"', "5", "null", '{"name": "Tea",', "[1, 2]"],
    ids=repr,
)
def test_b16_ac_1_8_body_message_is_exact(client: TestClient, content: str) -> None:
    """B16 / B15: every body rejection carries the exact body message."""
    assert_exact(post_raw(client, content), MSG_BODY)


def test_b16_ac_1_8_request_without_body_message_is_exact(client: TestClient) -> None:
    """B16 / B15: a POST with no body gets the exact body message."""
    assert_exact(client.post("/items"), MSG_BODY)


@pytest.mark.parametrize("name", [5, None, "", "   ", True, ["Tea"], {"a": 1}], ids=repr)
def test_b16_ac_1_8_name_message_is_exact(client: TestClient, name: Any) -> None:
    """B16 / B12: every bad name gets the exact name message."""
    assert_exact(client.post("/items", json=valid(name=name)), MSG_NAME)


def test_b16_ac_1_8_missing_name_message_is_exact(client: TestClient) -> None:
    """B16 / B12: missing name gets the exact name message."""
    assert_exact(client.post("/items", json=without("name")), MSG_NAME)


@pytest.mark.parametrize(
    "price", ["8.50", "3", "", None, True, False, -0.01, 8.505, -1, 1.001, [], {}], ids=repr
)
def test_b16_ac_1_8_price_message_is_exact(client: TestClient, price: Any) -> None:
    """B16 / B13: every bad price (str and bool included) gets the exact price message."""
    assert_exact(client.post("/items", json=valid(price=price)), MSG_PRICE)


def test_b16_ac_1_8_missing_price_message_is_exact(client: TestClient) -> None:
    """B16 / B13: missing price gets the exact price message."""
    assert_exact(client.post("/items", json=without("price")), MSG_PRICE)


@pytest.mark.parametrize("token", ["NaN", "Infinity", "-Infinity"])
def test_b16_ac_1_8_non_finite_price_message_is_exact(client: TestClient, token: str) -> None:
    """B16 / B13: NaN and Infinity get the exact price message."""
    response = post_raw(client, '{"name": "Tea", "price": ' + token + ', "quantity": 1}')
    assert_exact(response, MSG_PRICE)


@pytest.mark.parametrize("quantity", [8.0, "2", True, 0, -1, None, 1.5], ids=repr)
def test_b16_ac_1_8_quantity_message_is_exact(client: TestClient, quantity: Any) -> None:
    """B16 / B14: every bad quantity gets the exact quantity message."""
    assert_exact(client.post("/items", json=valid(quantity=quantity)), MSG_QUANTITY)


def test_b16_ac_1_8_missing_quantity_message_is_exact(client: TestClient) -> None:
    """B16 / B14: missing quantity gets the exact quantity message."""
    assert_exact(client.post("/items", json=without("quantity")), MSG_QUANTITY)


def test_b5_single_character_name_is_accepted(client: TestClient) -> None:
    """B5: one character is a valid name; a padded one is trimmed to it."""
    assert client.post("/items", json=valid(name="A")).json()["name"] == "A"
    assert client.post("/items", json=valid(name=" B ")).json()["name"] == "B"


def test_b6_price_zero_is_stored_as_decimal_zero(client: TestClient) -> None:
    """B6: price 0 is allowed and held as Decimal."""
    response = client.post("/items", json=valid(price=0))
    assert response.status_code == 201
    assert response.json()["price"] == 0
    assert stored()[0].price == Decimal(0)


def test_b6_two_decimals_accepted_three_rejected(client: TestClient) -> None:
    """B6: exactly 2 decimals pass, 3 do not."""
    ok = post_raw(client, '{"name":"Tea","price":1.25,"quantity":1}')
    assert ok.status_code == 201
    assert stored()[0].price == Decimal("1.25")
    bad = post_raw(client, '{"name":"Tea","price":1.255,"quantity":1}')
    assert bad.status_code == 400
    assert bad.json()["message"] == MSG_PRICE
    assert len(stored()) == 1


def test_b8_extra_fields_ignored_with_every_field_stored_exactly(client: TestClient) -> None:
    """B8: extras never reach the stored item or break the message of a real error."""
    ok = client.post("/items", json=valid(extra={"x": 1}, id=7, note="n"))
    assert ok.status_code == 201
    assert set(ok.json()) == {"id", "name", "price", "quantity"}
    bad = client.post("/items", json=valid(quantity=0, extra=1))
    assert bad.status_code == 400
    assert bad.json()["message"] == MSG_QUANTITY


def test_b1_module_store_is_a_cart_store_and_receives_posts() -> None:
    """B1 / B2: without the fixture swap the module store is a real CartStore."""
    module_store = cart.main.store
    assert isinstance(module_store, CartStore)
    before = len(module_store.list_all())
    plain = TestClient(cart.main.app)
    response = plain.post("/items", json=valid(name="Plain"))
    assert response.status_code == 201
    items = module_store.list_all()
    assert len(items) == before + 1
    assert items[-1].id == response.json()["id"]
    module_store._items.pop()


def test_b18_app_is_a_fastapi_app_with_title_and_error_handler() -> None:
    """B18: the module app is the configured FastAPI app and answers 400, not 422."""
    assert isinstance(cart.main.app, FastAPI)
    assert cart.main.app.title == "Shopping Cart API"
    response = TestClient(cart.main.app).post("/items", json={})
    assert response.status_code == 400


def _big_int() -> str:
    return "9" * 5000


def test_b15_b18_oversized_integer_quantity_is_a_body_error(client: TestClient) -> None:
    """B15 / B18: a 5000-digit integer cannot be parsed; exact body message, nothing stored."""
    assert_exact(post_raw(client, '{"name":"Tea","price":1,"quantity":' + _big_int() + "}"), MSG_BODY)


def test_b15_b18_oversized_integer_in_ignored_field_is_a_body_error(client: TestClient) -> None:
    """B15 / B18: the same for an extra field that would be ignored."""
    content = '{"name":"Tea","price":1,"quantity":1,"x":' + _big_int() + "}"
    assert_exact(post_raw(client, content), MSG_BODY)


def test_b18_unknown_path_keeps_the_framework_404_shape(client: TestClient) -> None:
    """B18 / Q1: 404 stays FastAPI's default body."""
    response = client.get("/nope")
    assert response.status_code == 404
    assert "detail" in response.json()
    assert "error" not in response.json()


def test_b18_wrong_method_keeps_the_framework_405_shape(client: TestClient) -> None:
    """B18 / Q1: 405 stays FastAPI's default body."""
    response = client.delete("/items")
    assert response.status_code == 405
    assert "detail" in response.json()
    assert "error" not in response.json()


def _probe_client() -> TestClient:
    from cart.errors import register_error_handlers

    probe = FastAPI()
    register_error_handlers(probe)

    @probe.get("/probe/{n}")
    def probe_n(n: int) -> dict[str, int]:
        return {"n": n}

    @probe.get("/q")
    def probe_q(name: int) -> dict[str, int]:
        return {"name": name}

    return TestClient(probe)


def test_b18_path_parameter_failure_names_the_parameter() -> None:
    """B18: a non-body location is named by its own parameter, as 400."""
    response = _probe_client().get("/probe/abc")
    assert response.status_code == 400
    assert response.json() == {"error": "validation_error", "message": "n is invalid"}


def test_b18_query_parameter_failure_names_the_parameter() -> None:
    """B18: a query failure says 'name is invalid', not the body name message."""
    response = _probe_client().get("/q", params={"name": "x"})
    assert response.status_code == 400
    assert response.json() == {"error": "validation_error", "message": "name is invalid"}
