---
sprint: 0
prd: [FR-2]
depends: [add-item]
estimate_days: 1
kind: internal
owner:
status: approved
scope: [src/cart/store.py, src/cart/errors.py, src/cart/main.py, tests/test_view_item.py]
touches: []
---
# View an item by id

## Intent

A developer needs to fetch one item by the id `POST /items` returned. Items come from add-item, so this intent depends on it; it adds `CartStore.get`, the 404 `not_found` error and `GET /items/{id}`. Done: S2 works by hand, and an unknown id answers 404 in the PRD's error shape.

## Non-goals

- Do not add update, delete or any endpoint the PRD does not list.
- Do not change `GET /items` or `POST /items`.
- Do not put the lookup in the route function: it lives in `CartStore.get`.
- Do not normalise the id (no lower-casing, no trimming) before looking it up.

## Design

| Part | Responsibility | Must not |
|---|---|---|
| `store.py` `CartStore.get` | look an item up by exact id under the store lock; raise `ItemNotFoundError` when absent | return None or change the cart |
| `errors.py` `ItemNotFoundError` and handler | carries the id; the handler answers 404 `not_found` in the error shape | import `store.py` |
| `main.py` | `GET /items/{id}` route calling `store.get` | hold the lookup rule |

## Interfaces

none

## Behaviours

- B1 (FR-2, AC-2.1, DR-1): GET /items/{id} with the id of an added item answers 200 with exactly the item returned at creation (the same four fields, same values, price as a number).
- B2 (FR-2, AC-2.2): GET /items/{id} with an id that is not in the cart answers 404 `{"error": "not_found", "message": "Item <id> not found"}`, where <id> is the requested id as sent (`/items/does-not-exist` gives "Item does-not-exist not found").
- B3 (FR-2, AC-2.2): `CartStore.get` raises `ItemNotFoundError` for an id it does not hold and never returns None.
- B4 (FR-2, AC-2.1): the lookup is an exact, case-sensitive string match: the held id in upper case is not found (proposed at chart).
- B5 (FR-2, AC-2.1): reading an item does not change the cart, and `get` takes the store lock so it never sees a half-added item (proposed at chart).

### Failure behaviour

- B6 (FR-2, AC-2.2): an id not in the cart, including a value that is not a UUID, answers 404 `not_found` with the message of B2, never 400 and never 500.

## Tests required

- B1, B2, B4, B6: end-to-end through `TestClient`, `tests/test_view_item.py`.
- B3, B5: unit, `tests/test_view_item.py` (against `CartStore` directly; `tests/test_store.py` belongs to add-item).

## Open questions

none
