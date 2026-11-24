# Store Tests

> Unit tests for the cart store behavior and invariants.

## Fixtures

The `client` fixture replaces `cart.main.store` with a fresh, empty `CartStore` via `monkeypatch`. [tests/conftest.py#client]
The fixture yields a `TestClient` wrapping `cart.main.app`. [tests/conftest.py#client]
The tests in `tests/test_store.py` build their own `CartStore()` and do not use this fixture. [tests/test_store.py]

## Item identity

`CartStore().add("Tea", Decimal(3), 1)` returns an item whose `id` parses as a UUID with version 4. [tests/test_store.py#test_b4_dr_2_id_is_canonical_uuid4]
The `id` equals `str()` of the parsed UUID, so it is in canonical lowercase hyphenated form. [tests/test_store.py#test_b4_dr_2_id_is_canonical_uuid4]
Fifty identical adds yield fifty distinct ids. [tests/test_store.py#test_b4_dr_2_ids_are_distinct_across_adds]
The signature of `CartStore.add` has exactly the parameters `self`, `name`, `price` and `quantity`. [tests/test_store.py#test_b4_dr_2_client_cannot_supply_an_id]
A caller therefore cannot pass an id to `add`. [tests/test_store.py#test_b4_dr_2_client_cannot_supply_an_id]

## Stored data

`add` returns an `Item`, and `list_all()` then equals a list holding that same item. [tests/test_store.py#test_b4_returned_item_is_the_stored_item]
The returned item keeps the `name`, `price` and `quantity` that were passed in. [tests/test_store.py#test_b4_returned_item_is_the_stored_item]
The `price` is a `decimal.Decimal` on the returned item and on the item read back from `list_all()`. [tests/test_store.py#test_b6_dr_4_price_is_stored_as_decimal]
A price of `Decimal("8.50")` compares equal to `Decimal("8.5")` after being stored. [tests/test_store.py#test_b6_dr_4_price_is_stored_as_decimal]
`list_all()` returns items oldest first, in insertion order. [tests/test_store.py#test_list_all_is_oldest_first]

## Snapshot semantics

`list_all()` returns a new list on every call. [tests/test_store.py#test_b10_nfr_1_list_all_returns_a_copy]
Clearing or appending to a returned list leaves the store's contents unchanged. [tests/test_store.py#test_b10_nfr_1_list_all_returns_a_copy]
A snapshot taken before a later `add` keeps its original length. [tests/test_store.py#test_b10_nfr_1_snapshot_is_unaffected_by_later_adds]
The store itself holds both items after that later `add`. [tests/test_store.py#test_b10_nfr_1_snapshot_is_unaffected_by_later_adds]

## Concurrency

One hundred threads are released together by a `threading.Barrier` and each calls `add`. [tests/test_store.py#test_b9_nfr_1_hundred_concurrent_adds_lose_nothing]
Afterwards the store holds 100 items with 100 distinct ids and all 100 expected names. [tests/test_store.py#test_b9_nfr_1_hundred_concurrent_adds_lose_nothing]
Four reader threads call `list_all()` in a loop while the main thread adds 300 items. [tests/test_store.py#test_b10_nfr_1_readers_never_see_a_half_added_item]
The readers record a problem if they see an item with an empty `id`, an empty `name`, a `quantity` below 1, or a duplicate id. [tests/test_store.py#test_b10_nfr_1_readers_never_see_a_half_added_item]
The test asserts that no problems were recorded and that the store ends with 300 items. [tests/test_store.py#test_b10_nfr_1_readers_never_see_a_half_added_item]

## Lock usage

`RecordingLock` is a duck-typed context manager that records `len(store._items)` on every enter and exit. [tests/test_store.py#RecordingLock]
Its `__enter__` appends the current item count to `enters`. [tests/test_store.py#RecordingLock.__enter__]
Its `__exit__` appends the current item count to `exits`. [tests/test_store.py#RecordingLock.__exit__]
With `RecordingLock` installed as `store._lock`, `add` enters the lock once, when the store holds 0 items. [tests/test_store.py#test_b10_nfr_1_add_holds_the_lock_around_draw_and_append]
`add` exits the lock when the store holds 1 item, so the append happens while the lock is held. [tests/test_store.py#test_b10_nfr_1_add_holds_the_lock_around_draw_and_append]
`list_all` enters and exits the same lock exactly once, each time seeing 1 item. [tests/test_store.py#test_b10_nfr_1_list_all_takes_the_lock_once]
With a real `threading.Lock` held by the test, calls to `add` and `list_all` from other threads stay blocked. [tests/test_store.py#test_b10_nfr_1_add_and_list_all_block_while_the_lock_is_held]
Both calls complete after the lock is released. [tests/test_store.py#test_b10_nfr_1_add_and_list_all_block_while_the_lock_is_held]

## Test map

```mermaid
flowchart LR
    Store["CartStore"] %% [tests/test_store.py#test_b4_returned_item_is_the_stored_item]
    Store --> Identity["id is uuid4, distinct, not client-supplied"] %% [tests/test_store.py#test_b4_dr_2_id_is_canonical_uuid4]
    Store --> Data["price is Decimal, list is oldest first"] %% [tests/test_store.py#test_b6_dr_4_price_is_stored_as_decimal]
    Store --> Snap["list_all returns a copy"] %% [tests/test_store.py#test_b10_nfr_1_list_all_returns_a_copy]
    Store --> Conc["100 concurrent adds lose nothing"] %% [tests/test_store.py#test_b9_nfr_1_hundred_concurrent_adds_lose_nothing]
    Store --> Lock["add and list_all take the lock"] %% [tests/test_store.py#test_b10_nfr_1_add_holds_the_lock_around_draw_and_append]
```
