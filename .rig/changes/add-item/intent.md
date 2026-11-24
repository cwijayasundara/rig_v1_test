---
slug: add-item
type: feature
source: .rig/product/sprints/sprint-0/intents/add-item.md
---
# Add an item to the cart

## Intent

A developer or script needs to put a new item in the one in-memory shopping cart with `POST /items`. Today the service only answers `GET /items` with `[]`, so nothing can be stored.

This change builds the whole write path that later intents stand on: the pydantic models, the thread-safe `CartStore` (with `list_all` as the read path that proves what was stored), the error shape, and the handler that turns every validation failure into 400 `validation_error` (never 422).

Done: PRD scenario S1 works by hand with curl, a rejected body stores nothing, 100 concurrent adds leave 100 items with 100 distinct ids, and pytest, ruff and mypy are clean.

## Open questions
none
