# Coverage, sprint 0

- failure covered source.md:47 "AC-1.3: WHEN name is missing, not a string, empty, or only whitespace THE SYSTEM SHALL respond 400 `validation_error` and store nothing"
- escalation n/a — no hand-off to a person; a client script calls the API
- ground-truth covered source.md:45 "AC-1.1: WHEN POST /items receives `{"name": "Coffee beans", "price": 8.5, "quantity": 2}` THE SYSTEM SHALL respond 201 with `{"id": "<id>", "name": "Coffee beans", "price": 8.5, "quantity": 2}` and store the item"
- security covered source.md:24 "No authentication, users or multiple carts: there is one cart per running process."
- rollout proposed — runs locally with `uv run uvicorn cart.main:app --port 8000`; no deploy, monitoring or rollback is defined (the source excludes Docker, CI and hosting)
- accuracy n/a — no model, agent or classifier in this product
- autonomy n/a — no model, agent or classifier in this product
- fallback n/a — no model, agent or classifier in this product
- budget n/a — no model, agent or classifier in this product
- audit n/a — no model, agent or classifier in this product
