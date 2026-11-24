# Test cases (.rig/product/sprints/sprint-0/testplan/cases.md)

| ID | Requirement | Intent | Behaviour | Level | Data | Expected | Access |
|---|---|---|---|---|---|---|---|
| TC-1 | FR-1, AC-1.1, DR-1 | add-item | B1 | holdout | data/add-valid.json | POST /items with the Coffee beans body answers 201 with exactly id, name, price 8.5 (a number), quantity 2 | - |
| TC-2 | FR-1, AC-1.1 | add-item | B2 | integration | data/add-valid.json | after the 201 the item is held by the store (list_all) | - |
| TC-3 | FR-1, AC-1.2 | add-item | B3 | integration | data/add-identical.json | two identical adds both answer 201 with different ids and both items are kept | - |
| TC-4 | FR-1, DR-2 | add-item | B4 | unit | data/store-ids.json | every id is a lowercase hyphenated UUID4 and ids are never reused | - |
| TC-5 | FR-1, DR-3 | add-item | B5 | integration | data/name-trim.json | name is trimmed at both ends and the inner double space is kept | - |
| TC-6 | FR-1, DR-4 | add-item | B6 | unit | data/price-values.json | CartStore.add accepts price 0 and holds the price as Decimal | - |
| TC-7 | FR-1, DR-5 | add-item | B7 | integration | data/quantity-large.json | quantity 1000000000000 and one past 2**64 are accepted | - |
| TC-8 | FR-1, AC-1.7 | add-item | B8 | integration | data/add-extra-fields.json | unknown fields are ignored and the server generates the id | - |
| TC-9 | NFR-1 | add-item | B9 | unit | data/concurrent.json | 100 concurrent adds leave exactly 100 items with 100 distinct ids | - |
| TC-10 | NFR-1 | add-item | B10 | unit | data/concurrent.json | list_all() returns a new list each call (mutating it leaves the store unchanged), and a reader thread running beside the 100 Barrier threads only ever sees whole four-field items (id, name, price, quantity) | - |
| TC-11 | NFR-2 | add-item | B11 | integration | - | uv run ruff check . and uv run mypy . report 0 errors | - |
| TC-12 | FR-1, AC-1.3 | add-item | B12 | integration | data/name-invalid.json | each invalid name answers 400 validation_error and stores nothing | - |
| TC-13 | FR-1, AC-1.4 | add-item | B13 | integration | data/price-invalid.json | each invalid price (including NaN and Infinity) answers 400 validation_error and stores nothing | - |
| TC-14 | FR-1, AC-1.5 | add-item | B14 | integration | data/quantity-invalid.json | each invalid quantity (8.0, "2", true, 0, -1) answers 400 validation_error and stores nothing | - |
| TC-15 | FR-1, AC-1.6 | add-item | B15 | integration | data/body-invalid.json | a body that is not valid JSON, is empty or is not an object answers 400 validation_error naming body and stores nothing | - |
| TC-16 | FR-1, AC-1.8 | add-item | B16 | integration | data/messages.json | the rejected quantity 0 body answers 400 with message "quantity must be an integer of at least 1" | - |
| TC-17 | FR-1, AC-1.8 | add-item | B17 | integration | data/messages.json | with several invalid fields the message names the first of name, price, quantity | - |
| TC-18 | FR-1, AC-1.3 | add-item | B18 | holdout | data/name-invalid.json | a body with no name answers 400, never 422, with exactly the keys error (validation_error) and message | - |
| TC-19 | FR-2, AC-2.1, DR-1 | view-item | B1 | holdout | data/view-known.json | GET /items/{id} answers 200 with exactly the item returned at creation | - |
| TC-20 | FR-2, AC-2.2 | view-item | B2 | holdout | data/view-unknown.json | GET /items/does-not-exist answers 404 {"error": "not_found", "message": "Item does-not-exist not found"} | - |
| TC-21 | FR-2, AC-2.2 | view-item | B3 | unit | data/view-unknown.json | CartStore.get raises ItemNotFoundError for an unknown id and never returns None | - |
| TC-22 | FR-2, AC-2.1 | view-item | B4 | integration | data/view-case.json | the held id in upper case answers 404 not_found | - |
| TC-23 | FR-2, AC-2.1 | view-item | B5 | unit | data/view-store.json | get leaves the cart unchanged: list_all() before and after is equal and a returned item is not a handle that alters the store | - |
| TC-24 | FR-2, AC-2.2 | view-item | B6 | integration | data/view-unknown.json | a well-formed UUID not in the cart and a non-UUID both answer 404 not_found, never 400 or 500 | - |
| TC-25 | FR-3, AC-3.1 | list-items | B1 | integration | data/list-empty.json | GET /items on a fresh cart answers 200 with [] | - |
| TC-26 | FR-3, AC-3.2, DR-1 | list-items | B2 | holdout | data/list-two.json | GET /items answers 200 with both items oldest first, each with exactly id, name, price, quantity | - |
| TC-27 | FR-3, AC-3.2 | list-items | B3 | integration | data/list-two.json | Tea added before Apples comes back Tea first, not sorted | - |
| TC-28 | FR-3, AC-3.3 | list-items | B4 | integration | data/list-two.json | two GET /items calls return the same body and the store is unchanged | - |
| TC-29 | FR-3, AC-3.2 | list-items | B5 | integration | data/list-query.json | ?limit=1 and ?sort=name are ignored: all items, same order | - |
| TC-30 | FR-1, DR-4 | add-item | B6 | integration | data/price-values.json | POST /items with price 8.50 sent as a JSON number answers 201 with price the JSON number 8.5, not a string | - |
