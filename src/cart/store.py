"""In-memory, thread-safe cart."""

import threading
import uuid
from decimal import Decimal

from cart.models import Item


class CartStore:
    """Holds items in insertion order; one lock guards every access."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._items: list[Item] = []

    def add(self, name: str, price: Decimal, quantity: int) -> Item:
        with self._lock:
            item = Item(id=str(uuid.uuid4()), name=name, price=price, quantity=quantity)
            self._items.append(item)
        return item

    def list_all(self) -> list[Item]:
        with self._lock:
            return list(self._items)
