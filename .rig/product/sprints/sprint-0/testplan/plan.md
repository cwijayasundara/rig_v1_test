# Test plan, sprint 0 (tier S)

## Strategy

- unit: CartStore behaviour (ids, Decimal price, lock, get) against the store directly in tests/test_store.py and tests/test_view_item.py.
- integration: every endpoint behaviour end to end through FastAPI TestClient; rejected bodies also check that nothing was stored; lint and types run as commands.
- holdout (acceptance, black box): one happy path per FR plus one case per error status (400 validation_error, 404 not_found), through the public HTTP interface only, in holdout/.
- No access cases: the PRD has no roles. No perf, security or manual levels: nothing external, no authentication.

## Environments and data

Local, Python 3.12 through uv, one in-memory cart per process; each test gets a fresh cart. Data is synthetic, in testplan/data/. Cases that depend on how a value is written (8.0, 8.50, NaN, Infinity, invalid JSON, empty body) keep the request body as a raw string under "raw". Boundaries: quantity past 2**64, name with an inner double space, price 0 and 8.505.

## Entry and exit criteria

Entry: the sprint chart is approved and each change has a spec. Exit: every case passes, `uv run pytest -q`, `uv run ruff check .` and `uv run mypy .` report no errors, and the holdout cases pass against the candidate revision.

## Regression scope

tests/test_api.py (GET /items on a fresh server returns []) and every test added by add-item, view-item and list-items must still pass.
