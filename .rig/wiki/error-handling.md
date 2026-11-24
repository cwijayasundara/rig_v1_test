# Error Handling

> Custom exception types and how they map to API responses.

## Exception types

`ItemNotFoundError` is the only custom exception class. [src/cart/errors.py#ItemNotFoundError]
It subclasses `Exception`. [src/cart/errors.py#ItemNotFoundError]
Its docstring says `CartStore.get` raises it when no held item has the requested id. [src/cart/errors.py#ItemNotFoundError]
It stores the id in its `item_id` attribute. [src/cart/errors.py#ItemNotFoundError.__init__]
The `get_item` route returns `store.get(item_id)`, so a missing item propagates to the registered handler. [src/cart/main.py#get_item]

## Registration

`register_error_handlers` attaches three handlers to the FastAPI app. [src/cart/errors.py#register_error_handlers]
The application calls it right after creating the `FastAPI` instance. [src/cart/main.py]
`RequestValidationError` is routed to `_validation_handler`. [src/cart/errors.py#register_error_handlers]
Starlette's `HTTPException` is routed to `_http_handler`. [src/cart/errors.py#register_error_handlers]
`ItemNotFoundError` is routed to `_not_found_handler`. [src/cart/errors.py#register_error_handlers]

## Response mapping

`_error_response` builds a 400 response with the body `{"error": "validation_error", "message": ...}`. [src/cart/errors.py#_error_response]
`_validation_handler` returns that 400 response for a request validation failure. [src/cart/errors.py#_validation_handler]
The module docstring states that validation errors return 400, never 422. [src/cart/errors.py]
`_http_handler` returns the same 400 `validation_error` response with the body message when the status is 400 and the detail is `There was an error parsing the body`. [src/cart/errors.py#_http_handler]
`_http_handler` delegates every other HTTP exception to FastAPI's default `http_exception_handler`. [src/cart/errors.py#_http_handler]
`_not_found_handler` returns status 404 with `{"error": "not_found", "message": "Item <id> not found"}`. [src/cart/errors.py#_not_found_handler]

## Validation messages

`_validation_message` selects the message for a validation failure. [src/cart/errors.py#_validation_message]
It collects the error locations whose first element is `body`. [src/cart/errors.py#_validation_message]
If there are no body errors but there are other errors, it returns `<last loc element> is invalid` for the first error. [src/cart/errors.py#_validation_message]
Otherwise it checks the fields in the order `name`, `price`, `quantity` and returns the message for the first invalid one. [src/cart/errors.py#_validation_message]
The `name` message is `name must be a non-empty string`. [src/cart/errors.py]
The `price` message is `price must be a number of at least 0 with at most 2 decimal places`. [src/cart/errors.py]
The `quantity` message is `quantity must be an integer of at least 1`. [src/cart/errors.py]
If no known field is invalid, the fallback message is `body must be a JSON object`. [src/cart/errors.py#_validation_message]

## Flow

```mermaid
flowchart TD %% [src/cart/errors.py#register_error_handlers]
    A[Request] --> B{Failure type} %% [src/cart/errors.py#register_error_handlers]
    B -->|RequestValidationError| C[_validation_handler] %% [src/cart/errors.py#_validation_handler]
    B -->|HTTPException| D[_http_handler] %% [src/cart/errors.py#_http_handler]
    B -->|ItemNotFoundError| E[_not_found_handler] %% [src/cart/errors.py#_not_found_handler]
    C --> F[400 validation_error] %% [src/cart/errors.py#_error_response]
    D -->|unparseable body| F %% [src/cart/errors.py#_http_handler]
    D -->|other status| G[FastAPI default handler] %% [src/cart/errors.py#_http_handler]
    E --> H[404 not_found] %% [src/cart/errors.py#_not_found_handler]
```
