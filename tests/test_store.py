"""CartStore unit tests (add-item: B4, B6, B9, B10)."""

import inspect
import threading
import uuid
from decimal import Decimal
from typing import Any, Self, cast

from cart.models import Item
from cart.store import CartStore


def test_b4_dr_2_id_is_canonical_uuid4() -> None:
    """B4 / DR-2: uuid version 4, canonical lowercase hyphenated."""
    item = CartStore().add("Tea", Decimal(3), 1)
    parsed = uuid.UUID(item.id)
    assert parsed.version == 4
    assert str(parsed) == item.id


def test_b4_dr_2_ids_are_distinct_across_adds() -> None:
    """B4 / DR-2 / AC-1.2: identical adds get different ids."""
    store = CartStore()
    ids = {store.add("Tea", Decimal(3), 1).id for _ in range(50)}
    assert len(ids) == 50


def test_b4_dr_2_client_cannot_supply_an_id() -> None:
    """B4 / DR-2: add takes no id parameter; the store generates it."""
    params = set(inspect.signature(CartStore.add).parameters)
    assert params == {"self", "name", "price", "quantity"}


def test_b4_returned_item_is_the_stored_item() -> None:
    """B4 / B2: add returns an Item that list_all then holds."""
    store = CartStore()
    item = store.add("Tea", Decimal(3), 2)
    assert isinstance(item, Item)
    assert store.list_all() == [item]
    assert (item.name, item.price, item.quantity) == ("Tea", Decimal(3), 2)


def test_b6_dr_4_price_is_stored_as_decimal() -> None:
    """B6 / DR-4: price is a decimal.Decimal."""
    store = CartStore()
    item = store.add("Tea", Decimal("8.50"), 1)
    assert isinstance(item.price, Decimal)
    assert isinstance(store.list_all()[0].price, Decimal)
    assert store.list_all()[0].price == Decimal("8.5")


def test_list_all_is_oldest_first() -> None:
    """Planned: list is oldest first."""
    store = CartStore()
    names = ["a", "b", "c"]
    for name in names:
        store.add(name, Decimal(1), 1)
    assert [i.name for i in store.list_all()] == names


def test_b9_nfr_1_hundred_concurrent_adds_lose_nothing() -> None:
    """B9 / NFR-1: 100 threads released together leave 100 items, 100 ids."""
    store = CartStore()
    barrier = threading.Barrier(100)

    def worker(n: int) -> None:
        barrier.wait()
        store.add(f"item-{n}", Decimal("1.00"), 1)

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    items = store.list_all()
    assert len(items) == 100
    assert len({i.id for i in items}) == 100
    assert {i.name for i in items} == {f"item-{n}" for n in range(100)}


def test_b10_nfr_1_list_all_returns_a_copy() -> None:
    """B10 / NFR-1: mutating the returned list does not change the store."""
    store = CartStore()
    store.add("Tea", Decimal(3), 1)
    snapshot = store.list_all()
    snapshot.clear()
    assert len(store.list_all()) == 1
    snapshot.append(store.list_all()[0])
    assert len(store.list_all()) == 1
    assert store.list_all() is not store.list_all()


def test_b10_nfr_1_snapshot_is_unaffected_by_later_adds() -> None:
    """B10 / NFR-1: an earlier snapshot does not grow when items are added."""
    store = CartStore()
    store.add("a", Decimal(1), 1)
    snapshot = store.list_all()
    store.add("b", Decimal(1), 1)
    assert len(snapshot) == 1
    assert len(store.list_all()) == 2


def test_b10_nfr_1_readers_never_see_a_half_added_item() -> None:
    """B10 / NFR-1: concurrent readers only see complete items."""
    store = CartStore()
    stop = threading.Event()
    bad: list[str] = []

    def reader() -> None:
        while not stop.is_set():
            snap = store.list_all()
            for item in snap:
                if not item.id or not item.name or item.quantity < 1:
                    bad.append(repr(item))
            if len({i.id for i in snap}) != len(snap):
                bad.append("duplicate id")

    readers = [threading.Thread(target=reader) for _ in range(4)]
    for t in readers:
        t.start()
    for n in range(300):
        store.add(f"item-{n}", Decimal(1), 1)
    stop.set()
    for t in readers:
        t.join()

    assert bad == []
    assert len(store.list_all()) == 300


class RecordingLock:
    """A duck-typed lock that records the store size at every enter and exit."""

    def __init__(self, store: CartStore) -> None:
        self.store = store
        self.enters: list[int] = []
        self.exits: list[int] = []

    def __enter__(self) -> Self:
        self.enters.append(len(self.store._items))
        return self

    def __exit__(self, *exc: object) -> None:
        self.exits.append(len(self.store._items))


def test_b10_nfr_1_add_holds_the_lock_around_draw_and_append() -> None:
    """B10: add takes the lock once; the append happens while it is held."""
    store = CartStore()
    recorder = RecordingLock(store)
    store._lock = cast(Any, recorder)
    store.add("Tea", Decimal(1), 1)
    assert recorder.enters == [0]
    assert recorder.exits == [1]


def test_b10_nfr_1_list_all_takes_the_lock_once() -> None:
    """B10: list_all acquires the same lock exactly once."""
    store = CartStore()
    store.add("Tea", Decimal(1), 1)
    recorder = RecordingLock(store)
    store._lock = cast(Any, recorder)
    assert len(store.list_all()) == 1
    assert recorder.enters == [1]
    assert recorder.exits == [1]


def test_b10_nfr_1_add_and_list_all_block_while_the_lock_is_held() -> None:
    """B10: with the store's lock held elsewhere, add and list_all wait for it."""
    store = CartStore()
    lock = threading.Lock()
    store._lock = lock
    done: list[str] = []

    def do_add() -> None:
        store.add("Tea", Decimal(1), 1)
        done.append("add")

    def do_list() -> None:
        store.list_all()
        done.append("list")

    lock.acquire()
    threads = [threading.Thread(target=do_add), threading.Thread(target=do_list)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(0.3)
    still_alive = [t.is_alive() for t in threads]
    lock.release()
    for t in threads:
        t.join(5)
    assert still_alive == [True, True]
    assert all(not t.is_alive() for t in threads)
    assert sorted(done) == ["add", "list"]
