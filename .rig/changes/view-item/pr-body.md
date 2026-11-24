## Review first

- Approved intent: chart-0 approved at af0855393dc4
- Highest consequence: tier 0, none of the signals; door: two-way
- Independent evidence: 2/2 hidden acceptance cases pass; verify pass
- Remaining uncertainty: 3 item(s), first: No agent reviewed this change (tier 0): the sensors and the tests are the evidence.
- Differential: not applicable
- Read in this order: src/cart/errors.py (source, 34 lines); src/cart/store.py (source, 8 lines); src/cart/main.py (source, 5 lines); tests/test_view_item.py (test, 129 lines); .rig/changes/view-item/plan.md (other, 35 lines); .rig/changes/view-item/spec.md (other, 25 lines); .rig/changes/view-item/evidence/runs.jsonl (other, 19 lines); .rig/changes/view-item/intent.md (other, 15 lines); and 6 more
- Flags: none

## Why the change

A developer who has added an item through `POST /items` has no way to read it back by id.

## Behaviours

- B1 (FR-2, AC-2.1, DR-1): GET /items/{id} with the id of an added item answers 200 with exactly the item returned at creation (the same four fields, same values, price as a number).
- B2 (FR-2, AC-2.2): GET /items/{id} with an id that is not in the cart answers 404 `{"error": "not_found", "message": "Item <id> not found"}`, where <id> is the requested id as sent (`/items/does-not-exist` gives "Item does-not-exist not found").
- B3 (FR-2, AC-2.2): `CartStore.get` raises `ItemNotFoundError` for an id it does not hold and never returns None.
- B4 (FR-2, AC-2.1): the lookup is an exact, case-sensitive string match: the held id in upper case is not found (proposed at chart).
- B5 (FR-2, AC-2.1): reading an item does not change the cart, and `get` takes the store lock so it never sees a half-added item (proposed at chart).
- B6 (FR-2, AC-2.2): an id not in the cart, including a value that is not a UUID, answers 404 `not_found` with the message of B2, never 400 and never 500.
- B7 (FR-2, C1): the handlers in `errors.py` narrow their exception type without `assert` (typed parameter, cast at registration), so the 400 and 404 answers are the same under `python -O`; the existing 400 `validation_error` answers do not change (carried C1; proposed at start).

## Plan changes after build

none

## Blast radius

- src/cart/store.py
- src/cart/errors.py
- src/cart/main.py
- tests/test_view_item.py

Door: two-way

## Dependents (computed)

4 file(s) outside the diff import the changed code, within two hops, by a static search of the import lines.

Existing tests that import the changed code, the regression set (4):
- tests/conftest.py (via src/cart/main.py)
- tests/test_add_item.py (via src/cart/errors.py)
- tests/test_api.py (via src/cart/main.py)
- tests/test_store.py (via src/cart/store.py)

## Risk

Tier 0: none of the signals

## How to revert

Revert the change: `git revert <sha>` for a plain commit on the trunk, or `git revert -m 1 <merge sha>` for a merge commit.

## What the checks would miss

No agent reviewed this change (tier 0): the sensors and the tests are the evidence.
- general-purpose (haiku): mypy reports four attr-defined errors until ItemNotFoundError and CartStore.get exist; the red run fails at collection rather than per test; the B6 %20 expectation assumes the decoded id.
- B3, B4, B5, B6, B7 are proved only by unit tests: no holdout case or approved journey names them

## Evidence

verify: pass on tree d8ca76d4cc0a9bb4 (no blocking sensors)
Holdout: 2/2 hidden acceptance cases pass

Red proof: the change's tests ran on the base code and failed (exit 2, `uv run pytest -q`):

```
___________________ ERROR collecting tests/test_view_item.py ___________________
E   ImportError: cannot import name 'ItemNotFoundError' from 'cart.errors' (/private/var/folders/mb/1p2b7y8n4lsdjfs7clvxf3080000gn/T/rig-red-MbyOiN/src/cart/errors.py)
ERROR tests/test_view_item.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 warning, 1 error in 0.05s
```

Weak red: the tests failed on a missing import, a missing symbol or a collection error, not an assertion. It shows they need the new code, not which behaviour fails without it.

Checks on the head tree (the latest verify's run of each):

- lint: pass, `All checks passed!`
- types: pass, `Success: no issues found in 10 source files`
- unit: pass, `150 passed, 1 warning in 1.05s`
- layers: pass, `layers: not enforced here (no approved layers config)`
- duplication: pass, `0`
- sast: pass, `sast: Semgrep does not run here (missing or broken), so CI scans this change (pipx install semgrep to scan locally)`
- audit: pass, `No known vulnerabilities found`
- mutation-diff: pass, `mutation: 9/10 killed on changed lines (score 0.90, min 0.8)`

Mutation: 9/10 on changed lines (score 0.90)

Every behaviour (B1, B2, B3, B4, B5, B6, B7) is named by a test this change adds or edits.

Tests frozen at dc2542b by the test writer

Rests on values nobody at the client said: B4 (marked), B5 (marked). Ask the owner to confirm them before merging.

## Check before approving

Answer these in your approving review, one line each (`Q1: <answer>`, 10+ characters; CI checks they are there; a sample of merged changes is audited):

Q1: What breaks if `__init__` in src/cart/errors.py returns early?
Q2: Which behaviour (B1, B2, B3, B4, B5, B6, B7) does src/cart/errors.py serve?
Q3: Which test fails if src/cart/errors.py lines 3-4 are reverted?

## Agents

- general-purpose on haiku: DONE_WITH_CONCERNS, 46366 tokens, 10 tool uses, 0.5 min
- general-purpose on haiku: DONE, 47866 tokens, 28 tool uses, 0.5 min

Total: 2 launches, 94232 tokens, 1.0 min

## Special things to note
- Carried C1 done: the `assert isinstance` lines in `errors.py` handlers are gone (typed parameters, `cast` at registration), so behaviour is the same under `python -O`.
- `store.py` now imports `ItemNotFoundError` from `errors.py`; `errors.py` does not import the store.
- The id is matched exactly as sent: no case folding or trimming.

## Change outline
- `src/cart/store.py`: `CartStore.get(item_id) -> Item`, exact match under the lock, raises `ItemNotFoundError`.
- `src/cart/errors.py`: `ItemNotFoundError(item_id)` and a 404 `not_found` handler.
- `src/cart/main.py`: `GET /items/{item_id} -> Item` calling `store.get`.
- `tests/test_view_item.py`: B1-B7.
