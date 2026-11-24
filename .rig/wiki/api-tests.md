# API Tests

> Tests that exercise the HTTP endpoints and response contracts.

## Overview

`tests/test_api.py` holds the HTTP-level tests for the cart API. [tests/test_api.py]
It imports `TestClient` from `fastapi.testclient` and `app` from `cart.main`. [tests/test_api.py]
It builds one module-level `TestClient` around that app. [tests/test_api.py]

## Smoke test

`test_smoke_empty_cart_lists_nothing` sends `GET /items`. [tests/test_api.py#test_smoke_empty_cart_lists_nothing]
It asserts the status code is 200. [tests/test_api.py#test_smoke_empty_cart_lists_nothing]
It asserts the JSON body equals an empty list. [tests/test_api.py#test_smoke_empty_cart_lists_nothing]
The test sends its request through the module-level client in `test_api.py`, not through the shared fixture. [tests/test_api.py]

## Shared fixture

`tests/conftest.py` defines a pytest fixture named `client`. [tests/conftest.py#client]
The fixture uses `monkeypatch` to replace `cart.main.store` with a new `CartStore()`. [tests/conftest.py#client]
It yields a `TestClient` over `cart.main.app`. [tests/conftest.py#client]
Tests that request this fixture run against an empty store. [tests/conftest.py#client]
`monkeypatch` reverts the `store` replacement when the test ends. [tests/conftest.py#client]
Tests in `test_api.py` that use the module-level client run against whatever `store` `cart.main` holds at that moment. [tests/test_api.py]

## Flow

```mermaid
flowchart LR
    T[test_smoke_empty_cart_lists_nothing] --> C[module-level TestClient] %% [tests/test_api.py]
    C --> A[cart.main app] %% [tests/test_api.py]
    F[client fixture] --> S[fresh CartStore] %% [tests/conftest.py#client]
    F --> A2[cart.main app] %% [tests/conftest.py#client]
```
