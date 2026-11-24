# Spec: View an item by id

## Behaviours
- B1 (FR-2, AC-2.1, DR-1): GET /items/{id} with the id of an added item answers 200 with exactly the item returned at creation (the same four fields, same values, price as a number).
- B2 (FR-2, AC-2.2): GET /items/{id} with an id that is not in the cart answers 404 `{"error": "not_found", "message": "Item <id> not found"}`, where <id> is the requested id as sent (`/items/does-not-exist` gives "Item does-not-exist not found").
- B3 (FR-2, AC-2.2): `CartStore.get` raises `ItemNotFoundError` for an id it does not hold and never returns None.
- B4 (FR-2, AC-2.1): the lookup is an exact, case-sensitive string match: the held id in upper case is not found (proposed at chart).
- B5 (FR-2, AC-2.1): reading an item does not change the cart, and `get` takes the store lock so it never sees a half-added item (proposed at chart).
- B6 (FR-2, AC-2.2): an id not in the cart, including a value that is not a UUID, answers 404 `not_found` with the message of B2, never 400 and never 500.

- B7 (FR-2, C1): the handlers in `errors.py` narrow their exception type without `assert` (typed parameter, cast at registration), so the 400 and 404 answers are the same under `python -O`; the existing 400 `validation_error` answers do not change (carried C1; proposed at start).

## Blast radius
- src/cart/store.py
- src/cart/errors.py
- src/cart/main.py
- tests/test_view_item.py

## Out of scope
- Update, delete or any endpoint the PRD does not list (intent non-goals).
- Any change to `GET /items` or `POST /items` answers.
- Normalising the id (lower-casing, trimming) before lookup.

## Open questions
none
