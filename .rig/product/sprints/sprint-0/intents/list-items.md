---
sprint: 0
prd: [FR-3]
depends: [view-item]
estimate_days: 1
kind: internal
owner:
status: approved
scope: [src/cart/main.py, tests/test_list_items.py]
touches: []
---
# View all items

## Intent

A developer needs to list the whole cart, oldest first. The items come from add-item (`CartStore.list_all` is already its read path); the dependency on view-item is only because both intents edit `main.py`, so this one builds after it. Done: S3 works by hand, and on a fresh server `GET /items` returns `[]`.

## Non-goals

- Do not add pagination, filtering or sorting options: query parameters are ignored.
- Do not change the store, the models or the errors.
- Do not add any endpoint the PRD does not list.

## Design

| Part | Responsibility | Must not |
|---|---|---|
| `main.py` `list_items` | replace the stub's `[]` with `store.list_all()` | sort, filter or change the cart |

## Interfaces

none

## Behaviours

- B1 (FR-3, AC-3.1): GET /items on an empty cart answers 200 with `[]`.
- B2 (FR-3, AC-3.2, DR-1): GET /items answers 200 with every item in the order they were added, oldest first, each with exactly the four fields id, name, price, quantity.
- B3 (FR-3, AC-3.2): the order is insertion order and never sorted: items added as "Tea" then "Apples" come back Tea first.
- B4 (FR-3, AC-3.3): GET /items does not change the cart: two calls in a row return the same body and `CartStore.list_all()` is unchanged.
- B5 (FR-3, AC-3.2): a query string such as `?limit=1` or `?sort=name` is ignored and all items are returned in the same order (proposed at chart).

### Failure behaviour

none: GET /items takes no body and no required input, so it has no 4xx case, and the store raises nothing on a read.

## Tests required

- B1 to B5: end-to-end through `TestClient`, `tests/test_list_items.py` (items added through POST /items; B4 also compares `cart.main.store.list_all()` before and after).

## Open questions

none
