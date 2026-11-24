# Plan: Add an item to the cart

## Files
- src/cart/models.py (new): the request and item models
- src/cart/store.py (new): the in-memory cart store
- src/cart/errors.py (new): error body and the validation handler
- src/cart/main.py (changed): module-level store, the POST route, handler registration; the GET route untouched
- tests/conftest.py (new): client fixture swapping a fresh store into the app module
- tests/test_add_item.py, tests/test_store.py (new)

## Phases
- [x] Phase 1: store and models. Failing unit tests first and seen red, then `Item` and `CartStore` (B4, B6, B9, B10); verify with `uv run pytest tests/test_store.py`
- [x] Phase 2: happy path. Conftest fixture and failing end-to-end tests first and seen red, then `ItemCreate` and `POST /items` 201 (B1, B2, B3, B5, B6, B7, B8); verify with `uv run pytest tests/test_add_item.py`
- [x] Phase 3: rejection. Failing tests first and seen red, then validators and the 400 handler (B12 to B18); verify with the full suite, ruff and mypy

## Interfaces
Design rows of the intent (`## Design` in the charted intent) are the contract; signatures:
- `ItemCreate(name: str, price: Decimal, quantity: int)`: `extra="ignore"`; name strict str, stripped, min length 1; quantity strict int (rejects bool, 8.0, "2"), `ge=1`; price lax Decimal with a before-validator that rejects str and bool, then `ge=0`, `decimal_places=2`, finite (strict Decimal would reject the float 8.5).
- `Item(id: str, name: str, price: Decimal, quantity: int)`: price serialises to a JSON number.
- `CartStore.add(name: str, price: Decimal, quantity: int) -> Item`: one `threading.Lock` around `uuid4` draw and append. `CartStore.list_all() -> list[Item]`: same lock, returns a copy.
- `errors.py`: `error_body(code: str, message: str) -> dict[str, str]`; `register_error_handlers(app: FastAPI) -> None` maps `RequestValidationError` to 400 `validation_error`, message "<field> must be ..." for the first invalid field in order name, price, quantity, or naming `body` for invalid JSON, empty or non-object bodies.
- `POST /items -> 201 Item`; the route only calls `store.add`.

## Tests
- B1, B3, B5, B7, B8, B16: tests/test_add_item.py, end-to-end; B7 also quantity 1 accepted
- B6 (via the route): tests/test_add_item.py, end-to-end: price 0 and 8.99 answer 201 and price returns as a JSON number
- B2, B12, B13, B14, B15, B17: tests/test_add_item.py, end-to-end, reading `cart.main.store.list_all()` for stored and stores nothing
- B18: tests/test_add_item.py, end-to-end (status 400, body keys exactly error and message)
- B4, B6, B9, B10: tests/test_store.py, unit (B9 with 100 threads released by a `threading.Barrier`; B10 copy returned and lock held during add)
- B11: sensors lint and types, no test line

## Contracts
- POST /items: request {name: string, price: number, quantity: integer}, unknown fields ignored; 201 {id, name, price, quantity}; 400 {"error": "validation_error", "message": string}. No contract file is edited.

## Verification
- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy .`
- By hand: `uv run uvicorn cart.main:app --port 8000` then curl the PRD S1 body and a bad body

## Decisions
- The existing smoke test of the GET route is unaffected (that route is untouched).
- Kept the sprint implementation-plan tasks for add-item (failing test, then code) and grouped them into three phases that each cross layers.
- Strictness is per field (see Interfaces), not model-wide; the handler translates errors into the field message, so no business logic enters the route.
- 404 and 405 stay framework defaults (intent Q1).

## Open questions
none
