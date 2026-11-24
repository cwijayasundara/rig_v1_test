# Plan: View an item by id

## Files
- src/cart/store.py: add the `get` method
- src/cart/errors.py: add `ItemNotFoundError`, its 404 handler; drop `assert` from handlers (C1)
- src/cart/main.py: add `GET /items/{item_id}`
- tests/test_view_item.py: new. No existing test pins changed behaviour (every test directory checked).

## Interfaces
Design rows: intent.md `## Design` (store, errors, main), cited not restated.
- `CartStore.get(item_id: str) -> Item`: exact match under the lock; raises `ItemNotFoundError`.
- `ItemNotFoundError(item_id: str)`, attribute `item_id`; handler answers 404 `{"error": "not_found", "message": "Item <id> not found"}`.
- `GET /items/{item_id} -> 200 Item`.
- Handlers take `Exception`-typed params narrowed by `cast` inside registration wrappers, no `assert`.

## Tests
- B1: tests/test_view_item.py, end-to-end (fetched body equals the 201 body)
- B2: tests/test_view_item.py, end-to-end (404 body, message uses id as sent)
- B3: tests/test_view_item.py, unit (raises, never None)
- B4: tests/test_view_item.py, end-to-end (upper-cased id gives 404)
- B5: tests/test_view_item.py, unit (cart unchanged after get; get blocks while the lock is held)
- B6: tests/test_view_item.py, end-to-end (non-UUID id gives 404, not 400/500)
- B7: tests/test_view_item.py, unit (errors.py has no Assert node; invalid POST body still 400 validation_error)

## Contracts
none

## Verification
- `uv run pytest -q`, `uv run ruff check .`, `uv run mypy .`

## Decisions
- Kept the implementation-plan.md task order (store first, then route). B7 added at start for carried C1.

## Open questions
none
