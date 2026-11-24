# Shopping Cart API

rig is on in this repo: work from the request as usual, and its checks and guides run on every turn; /rig:start is the full workflow (spec, plan, approval), used only when the person asks for it. Use superpowers skills only when an sdlc skill names one.

## What this is

A small FastAPI service holding one in-memory shopping cart (add item, get item by id, list items). Greenfield; sprint 0 PRD is `docs/prd/sprint-0/prd.md`.
Python 3.12, FastAPI + uvicorn, uv, pytest, ruff, mypy.

## Map

- `src/cart/main.py`: FastAPI app and routes (currently only `GET /items` returning `[]`)
- `tests/test_api.py`: API smoke test via `TestClient`
- `pyproject.toml`, `uv.lock`: dependencies and tool config; `Makefile`: `test`, `test-fast`, `lint`, `types`
- `docs/prd/sprint-0/prd.md`: the PRD
- `.rig/sensors.json`: sensor registry; `.rig/guides/`: guides; `.claude/commands/rig/`: rig commands; `.claude/agents/`: rig agents

## Commands

- Test: `uv run pytest -q` (fast: `make test-fast`)
- Lint: `uv run ruff check .`
- Types: `uv run mypy .`
- Run: `uv run uvicorn cart.main:app --port 8000`

## Conventions

- Business logic lives in `store.py` (planned), never in route functions.
- Money is `decimal.Decimal`, never float.
- Run pytest, ruff and mypy before finishing.

## Gotchas

- Ask first before adding a runtime dependency beyond fastapi and uvicorn, or changing a response shape.
- Never add persistence or endpoints the PRD does not list.
- ruff and mypy exclude `.rig/` and `.claude/`.

## Planned (from the PRD)

- `models.py` (pydantic models), `store.py` (in-memory cart, thread-safe), `errors.py`; `tests/test_store.py`.
- `POST /items`, `GET /items/{id}`; errors as `{"error", "message"}` with 400 `validation_error` (never 422) and 404 `not_found`.
- Item ids are UUID4 strings; list is oldest first; unknown body fields are ignored.

## Review

- Flag any API, schema or event change that the change's plan.md `## Contracts` does not announce.
- Flag anything the brief's non-goals exclude.

# Compact instructions

Keep the active sdlc change, failing tests and file paths; drop exploration output.

<!-- rig:guides start hash=2c1d973f899996fc -->
- Ruff must pass on every file you touch; fix the code rather than the rule. [sensor:lint]
- The project must type-check with mypy before the turn ends. [sensor:types]
- Run pytest before claiming done; fix the code, never the tests. [sensor:unit]
- Respect the approved layers in architecture.md; do not import across a forbidden boundary. [sensor:layers]
- Reuse existing code instead of copying it; the duplicated share may not grow past its baseline. [sensor:duplication]
- Semgrep scans the source files this change touches for security bugs (injection, unsafe input, secrets, weak crypto); fix the code rather than silencing the rule. [sensor:sast]
- Do not add dependencies with known vulnerabilities. [sensor:audit]
- Every line this change adds is pinned by a test: the mutation score on the changed lines must reach mutation.minScore; a survivor names a line and a change no test noticed, and goes back to the test writer. [sensor:mutation-diff]
- Tests must assert behaviour so that changing the code makes them fail. [sensor:mutation]
- Never write credentials into the repo; read them from the environment. [sensor:secrets]
- Fix the code, never the test: do not skip, delete or weaken tests or lower coverage thresholds. [sensor:test-tamper]
- Do not silence a lint or type error without a reason on the same line. [sensor:suppression]
- Do not weaken .rig/sensors.json, .rig/rules.json or frozen contract files; ask a person to waive instead. [sensor:harness-tamper]
- Keep files, diffs and lines under the size limits; the size finding names each file and line over the limit, so fix those rather than searching for them. [sensor:size]
- Respect the declared layer rules; do not import across a forbidden boundary. [sensor:layering]
- Follow the project rules in .rig/rules.json. [sensor:rules]
- A new test must fail before the change and pass after it. [sensor:red-proof]
- Every behaviour in the change spec.md needs a test that names its B-number; brief behaviours with no test yet only warn. [sensor:traceability]
- Build on the build model; leave diff review to the /rig:pr reviewer; the evaluator agent reviews charts, plans and test plans. [sensor:model-role]
<!-- rig:guides end -->
