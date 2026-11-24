# Wiki

- [Cart Service Overview](cart-service-overview.md): High-level introduction to the cart package: what it does, how the modules fit together, and how a request flows from API to store. (built 991098f)
  - [HTTP API](http-api.md): The application entry point and its endpoints: routing, request/response handling, and how errors are surfaced to clients. (built 4043a3c)
  - [Domain Models](domain-models.md): Data models for carts and items: fields, validation rules, and how they are used across the service. (built 991098f)
  - [Cart Store](cart-store.md): Storage layer that holds cart state and implements item operations; persistence semantics and invariants. (built 4043a3c)
  - [Error Handling](error-handling.md): Custom exception types and how they map to API responses. (built 4043a3c)
  - [Add Item Flow](add-item-flow.md): End-to-end walkthrough of adding an item to a cart: API call, validation, store mutation, and error cases. (built 4043a3c)
- [Testing Guide](testing-guide.md): How the test suite is organized, shared fixtures, and how to run and extend tests. (built 4043a3c)
  - [API Tests](api-tests.md): Tests that exercise the HTTP endpoints and response contracts. (built 991098f)
  - [Store Tests](store-tests.md): Unit tests for the cart store behavior and invariants. (built 991098f)
  - [Add Item Tests](add-item-tests.md): Frozen acceptance tests for the add-item feature and the behaviors they pin down. (built 991098f)
