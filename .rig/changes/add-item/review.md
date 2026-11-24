verdict: changes-needed

## Findings
- [severity: medium] [category: correctness] src/cart/models.py:26: price is read through a float and returned through float(), so a valid 2-decimal price above about 15 digits loses cents (12345678901234567.89 is stored as 12345678901234568). Fails when: price has more than about 15 significant digits. → fix: parse the raw JSON number as Decimal and write the Decimal into JSON exactly; left open for a person: it changes how the body is read and the response is written, which CLAUDE.md says to ask about first
- [severity: medium] [category: unmapped] src/cart/errors.py, src/cart/models.py: public names validation_message, error_body, Name, Price, Quantity were not in the intent's Design → fixed (confirmed)
- [severity: medium] [category: coupling] src/cart/errors.py:24: handler ignored loc[0] and gave non-body errors the body message → fixed (confirmed)
- [severity: medium] [category: tests] tests/test_store.py: the lock tests passed with the lock removed → fixed (confirmed)
- [severity: medium] [category: security] src/cart/errors.py: a 4301+ digit integer made FastAPI answer {"detail": ...} instead of the error shape → fixed (confirmed)
- [severity: medium] [category: security] src/cart/models.py:24: name has no max length and the body has no size limit; a 2,000,000 character name is accepted and echoed. Fails when: a client sends very large names repeatedly. → fix: add max_length and a body-size limit; left open for a person: PRD/spec do not set a limit and it changes the response contract (CLAUDE.md: ask first)
- [severity: medium] [category: security] src/cart/store.py:20: no cap on item count, and B7 says quantity has no upper limit, so memory grows without bound. Fails when: a client loops POST /items. → fix: decide a cap or record the accepted risk in the PRD; left open for a person: B7 says "no upper limit"

## Dismissed

## Deferred
- src/cart/errors.py: assert isinstance in the handlers disappears under python -O; type the parameter and cast at registration
- src/cart/models.py:19: the PydanticCustomError text is never shown because the handler writes its own message
- src/cart/models.py:49: lambda value: float(value) could be float
- price -0.0 passes ge=0 and is returned as -0.0

## Unverifiable
- Whether JSON prices with an exponent (1e2) are meant to be accepted → settle by: a PRD decision plus a test
- Whether a non-JSON content type with a valid JSON object body should be accepted → settle by: a journey with curl
- Whether uvicorn or a proxy limits body size in the real deployment → settle by: a live config

## Pre-existing

## One thing
Three open items (price exactness, name and body size limits, item and quantity cap) are decisions for a person, not code fixes.
