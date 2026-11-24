from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

import cart.main
from cart.store import CartStore


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """A TestClient over the app with a fresh, empty CartStore swapped in."""
    monkeypatch.setattr(cart.main, "store", CartStore())
    yield TestClient(cart.main.app)
