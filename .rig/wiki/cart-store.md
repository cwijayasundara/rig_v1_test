# Cart Store

> Storage layer that holds cart state and implements item operations; persistence semantics and invariants.

## Overview

The module provides an in-memory, thread-safe cart. [src/cart/store.py]
`CartStore` holds items in insertion order. [src/cart/store.py#CartStore]
One lock guards every access to the item list. [src/cart/store.py#CartStore]

## State and persistence

Each `CartStore` instance keeps its items in a private Python list. [src/cart/store.py#CartStore.__init__]
The constructor creates a `threading.Lock` and an empty list. [src/cart/store.py#CartStore.__init__]
The file does no disk or database access. [src/cart/store.py]
Items exist only in the memory of the owning `CartStore` instance. [src/cart/store.py#CartStore]
The store offers no operation to remove, update or clear items. [src/cart/store.py#CartStore]

## Operations

### add

`add` takes a name, a `Decimal` price and an integer quantity, and returns the created `Item`. [src/cart/store.py#CartStore.add]
It acquires the lock before creating the item. [src/cart/store.py#CartStore.add]
It generates the item id as the string form of a `uuid.uuid4()` value. [src/cart/store.py#CartStore.add]
It appends the new item to the end of the list. [src/cart/store.py#CartStore.add]
It returns the item after the lock is released. [src/cart/store.py#CartStore.add]
It does not validate name, price or quantity. [src/cart/store.py#CartStore.add]

### get

`get` takes an item id string and returns the matching `Item`. [src/cart/store.py#CartStore.get]
It scans the list in insertion order while holding the lock. [src/cart/store.py#CartStore.get]
It returns the first item whose id equals the requested id. [src/cart/store.py#CartStore.get]
It raises `ItemNotFoundError` with the requested id when no item matches. [src/cart/store.py#CartStore.get]
The exception is raised after the lock is released. [src/cart/store.py#CartStore.get]

### list_all

`list_all` returns every item in insertion order. [src/cart/store.py#CartStore.list_all]
It builds the result with `list(self._items)` while holding the lock. [src/cart/store.py#CartStore.list_all]
The returned list is a new list, so changing it does not change the store's list. [src/cart/store.py#CartStore.list_all]
The list contains the stored `Item` objects themselves, not copies. [src/cart/store.py#CartStore.list_all]

## Invariants

All three operations take the same `threading.Lock` before touching the item list. [src/cart/store.py#CartStore]
Because the lock is a plain `threading.Lock`, a thread that holds it cannot acquire it again. [src/cart/store.py#CartStore.__init__]
Item order in the list is the order in which `add` calls acquired the lock. [src/cart/store.py#CartStore.add]
Ids come from `uuid.uuid4()`, and `add` does not check them against existing ids. [src/cart/store.py#CartStore.add]
