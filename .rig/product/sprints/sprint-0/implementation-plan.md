---
sprint: 0
updated: 2026-11-24
---
# Sprint 0 implementation plan

**Goal:** ship a FastAPI service holding one in-memory shopping cart: add an item, fetch it by id, list all items, with errors in the PRD's shape.

**Architecture:** `main.py` holds the routes and one module-level `CartStore`; `models.py` validates and shapes items; `errors.py` turns failures into `{"error", "message"}` bodies. Dependencies point from `main.py` to the others, never back. See `.rig/product/architecture.md`.

**Tech stack:** Python 3.12, FastAPI (pydantic v2), uvicorn, uv; pytest with `TestClient` (httpx), ruff, mypy.

**Design:** none (tier S)

## Global constraints

- Business logic (validation, ids, ordering, locking) lives in `models.py` and `store.py`, never in a route function.
- Money is `decimal.Decimal`, never float; the price becomes a JSON number only when the response is serialised.
- Every error is `{"error": "<code>", "message": "<text>"}`: `validation_error` is 400 (never 422), `not_found` is 404.
- NFR-1: 100 concurrent adds leave exactly 100 items with 100 distinct ids. NFR-2: ruff and mypy report 0 errors.
- No new runtime dependency beyond fastapi and uvicorn; no persistence; no endpoint the PRD does not list.

## Review focus

- The id draw and the append sit in one critical section, and reads take the same lock.
- Strictness of `ItemCreate`: bool, "8.50", 8.0 as quantity, 8.505 and negative price must be rejected; pydantic coerces by default.
- The 400 handler covers invalid JSON and a non-object body, and its message names the field.
- A rejected add leaves the store untouched; `GET /items` never mutates.

## Allocation

| Lane | Intents | Days | Suits | Why |
|---|---|---|---|---|
| 1 | add-item → view-item → list-items | 4 | senior | add-item holds the concurrency and the interfaces the other two build on; the PRD gives one engineer |

## Intents

### add-item

Depends on: none · Estimate: 2 · Suits: senior

Files: `src/cart/models.py`, `src/cart/store.py`, `src/cart/errors.py`, `src/cart/main.py` (changed); tests: `tests/conftest.py`, `tests/test_add_item.py`, `tests/test_store.py`.

Interfaces: `ItemCreate(name: str, price: Decimal, quantity: int)`; `Item(id: str, name: str, price: Decimal, quantity: int)` (price serialises to a JSON number); `CartStore.add(name, price, quantity) -> Item`; `CartStore.list_all() -> list[Item]`; `register_error_handlers(app: FastAPI) -> None`; `POST /items -> 201 Item`.

- [ ] B4, B6, B9, B10: write failing store tests in `tests/test_store.py` (UUID4 canonical id, Decimal price, 100 threads released by a Barrier, `list_all` returns a copy); run and see them fail
- [ ] B2, B4, B6, B9, B10: implement `Item` in `models.py` and `CartStore` in `store.py` (one `threading.Lock` around the id draw and append); the tests pass
- [ ] B1, B3, B5, B7, B8: add the `client` fixture in `tests/conftest.py` and write failing tests in `tests/test_add_item.py` (example body, identical adds, trim, huge quantity, extra `id` ignored); run and see them fail
- [ ] B1, B3, B5, B7, B8: implement `ItemCreate` (strict, trims name, ignores extras) and `POST /items` in `main.py` (201); the tests pass
- [ ] B12, B13, B14, B15, B16, B17, B18: write failing tests (each bad name, price, quantity and body shape; stored nothing via `list_all`; message text; two bad fields; status 400 never 422); run and see them fail
- [ ] B12, B13, B14, B15, B16, B17, B18: implement the validators and `register_error_handlers` in `errors.py`, register it in `main.py`; the tests pass
- [ ] B11: run `uv run pytest -q`, `uv run ruff check .` and `uv run mypy .`; all clean

### view-item

Depends on: add-item · Estimate: 1 · Suits: any

Files: `src/cart/store.py`, `src/cart/errors.py`, `src/cart/main.py` (changed); tests: `tests/test_view_item.py`.

Interfaces: `CartStore.get(item_id: str) -> Item` (raises `ItemNotFoundError`); `ItemNotFoundError(item_id: str)` with a 404 `not_found` handler; `GET /items/{item_id} -> 200 Item`.

- [ ] B3, B5: write failing store-level tests in `tests/test_view_item.py` (get raises for an absent id, reads leave the cart unchanged); run and see them fail
- [ ] B3, B5: implement `CartStore.get` under the lock and `ItemNotFoundError`; the tests pass
- [ ] B1, B2, B4, B6: write failing end-to-end tests (added item fetched equals the 201 body, unknown id gives the 404 body, upper-cased id not found, non-UUID id is 404); run and see them fail
- [ ] B1, B2, B4, B6: implement the not_found handler in `errors.py` and `GET /items/{item_id}` in `main.py`; the tests pass
- [ ] run `uv run pytest -q`, `uv run ruff check .` and `uv run mypy .`; all clean

### list-items

Depends on: view-item · Estimate: 1 · Suits: any

Files: `src/cart/main.py` (changed); tests: `tests/test_list_items.py`.

Interfaces: `GET /items -> 200 list[Item]` (the stub's `[]` is replaced by `store.list_all()`).

- [ ] B1, B2, B3, B4, B5: write failing tests in `tests/test_list_items.py` (empty gives `[]`, two adds come back oldest first, Tea before Apples, repeated reads identical, `?limit=1` ignored); run and see them fail (B1 may already pass: the stub returns `[]`)
- [ ] B1, B2, B3, B4, B5: implement `list_items` in `main.py` as `store.list_all()`; the tests pass
- [ ] run `uv run pytest -q` (the smoke test in `tests/test_api.py` still passes), `uv run ruff check .` and `uv run mypy .`; all clean
