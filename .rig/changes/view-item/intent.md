---
slug: view-item
type: feature
source: .rig/product/sprints/sprint-0/intents/view-item.md
---
# View an item by id

## Intent

A developer who has added an item through `POST /items` has no way to read it back by id. They need `GET /items/{id}` to return exactly that item, and a 404 `not_found` in the PRD's error shape when the id is not in the cart.

Done: the id returned at creation fetches the same four-field item (S2 by hand), an unknown id, even one that is not a UUID, answers 404 `Item <id> not found`, the lookup lives in `CartStore.get` under the store lock, and the carried C1 cleanup removes `assert` from the error handlers.

## Open questions
none
