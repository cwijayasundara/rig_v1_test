# Product brief

## Context and intent

A small FastAPI service holds one shopping cart in memory. A developer or script adds items with POST /items, fetches one with GET /items/{id} and lists all with GET /items. Success: the PRD's three scenarios work with curl and `uv run pytest -q`, `ruff check .` and `mypy .` pass. Greenfield; nothing depends on it.

## Non-goals

- Do not add authentication, users or multiple carts: one cart per running process.
- Do not add update or delete of items (delete arrives in sprint 1).
- Do not add checkout, payment, tax, discounts, totals or currency handling.
- Do not add persistence: a restart empties the cart.
- Do not add a UI, pagination, filtering or sorting options.
- Do not add endpoints the PRD does not list.

## Architecture

See `.rig/product/architecture.md` (modules, flows, quality tactics) and `.rig/product/adr/` (ADR-0001, the item id format).

## Constraints

- Python 3.12, FastAPI on uvicorn, uv, pytest (TestClient, httpx), ruff, mypy.
- Business logic in `store.py` and `models.py`, never in route functions; price is `decimal.Decimal`, never float.
- Ask first before adding a runtime dependency beyond fastapi and uvicorn, or changing a response shape.
- NFR-1: 100 concurrent adds leave exactly 100 items with 100 distinct ids. NFR-2: 0 errors from ruff and mypy.

## Interfaces

- `POST /items` (201), `GET /items/{id}` (200, 404), `GET /items` (200); errors are `{"error", "message"}` with 400 `validation_error` (never 422) and 404 `not_found`. The PRD's Examples section fixes the shapes; no contract file.

## Behaviours

see the intents

### Failure behaviour

see the intents

## Tests required

see the intents
