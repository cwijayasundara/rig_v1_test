# Add Item Flow

> End-to-end walkthrough of adding an item to a cart: API call, validation, store mutation, and error cases.

## Overview

The `add_item` route handles `POST /items` and answers with status 201 on success. [src/cart/main.py#add_item]
The module builds one `FastAPI` app titled "Shopping Cart API" and registers the error handlers on it. [src/cart/main.py]
A single module-level `CartStore` instance holds the cart. [src/cart/main.py]

```mermaid
flowchart TD %% [src/cart/main.py#add_item]
    A["POST /items"] --> B["ItemCreate validation"] %% [src/cart/models.py#ItemCreate]
    B -->|valid| C["CartStore.add"] %% [src/cart/store.py#CartStore.add]
    C --> D["201 with Item"] %% [src/cart/main.py#add_item]
    B -->|invalid| E["_validation_handler"] %% [src/cart/errors.py#_validation_handler]
    E --> F["400 validation_error"] %% [src/cart/errors.py#_error_response]
```

## API call

`add_item` takes its `body` parameter as an `ItemCreate` and returns an `Item`. [src/cart/main.py#add_item]
It passes the body's `name`, `price` and `quantity` to the store's `add` method. [src/cart/main.py#add_item]
The response model is `Item`, which carries `id`, `name`, `price` and `quantity`. [src/cart/models.py#Item]
`Item` serializes `price` as a JSON number, not a string. [src/cart/models.py#Item]

## Validation

All request validation rules live in the models module. [src/cart/models.py]
`ItemCreate` ignores unknown fields, so an extra field neither fails the request nor reaches the stored item. [src/cart/models.py#ItemCreate]
`name` must be a strict string, is stripped of surrounding whitespace, and must have at least one character. [src/cart/models.py#ItemCreate]
`price` is a `Decimal` of at least 0 with at most 2 decimal places, and NaN and infinity are not allowed. [src/cart/models.py#ItemCreate]
Before the numeric checks run, strings and booleans are rejected as prices with the message "price must be a number". [src/cart/models.py#_reject_non_numbers]
`quantity` must be a strict integer of at least 1. [src/cart/models.py#ItemCreate]

## Store mutation

`CartStore.add` takes the store lock before it builds or appends anything. [src/cart/store.py#CartStore.add]
It creates an `Item` with a new `uuid4` string as its id, so a client-supplied id is never used. [src/cart/store.py#CartStore.add]
It appends the item to the in-memory list and returns it. [src/cart/store.py#CartStore.add]
Two identical adds produce two separate items with different ids. [src/cart/store.py#CartStore.add]
`CartStore.list_all` returns a copy of the items in insertion order while holding the same lock. [src/cart/store.py#CartStore.list_all]

## Error cases

`register_error_handlers` installs handlers for `RequestValidationError`, Starlette's `HTTPException` and `ItemNotFoundError`. [src/cart/errors.py#register_error_handlers]
Validation failures return status 400, never 422. [src/cart/errors.py#_error_response]
The 400 body has exactly two keys: `error`, set to `validation_error`, and `message`. [src/cart/errors.py#_error_response]
A validation failure leaves the store unchanged, because `add` is only reached once validation has passed. [src/cart/main.py#add_item]

### Choosing the message

`_validation_message` looks at the errors located in the request body and names the first invalid field in the order `name`, `price`, `quantity`. [src/cart/errors.py#_validation_message]
Each field has one fixed message. [src/cart/errors.py#_validation_message]
A failure outside the body, such as in a path or query parameter, yields "<parameter> is invalid". [src/cart/errors.py#_validation_message]

### Unparseable bodies

A 400 `HTTPException` with the detail "There was an error parsing the body" is rewritten to the same `validation_error` shape with the body message. [src/cart/errors.py#_http_handler]
Any other `HTTPException` is passed to FastAPI's default handler, so its response shape is unchanged. [src/cart/errors.py#_http_handler]

### Unknown ids

`ItemNotFoundError` is not raised by `add`; `CartStore.get` raises it when no held item has the requested id. [src/cart/store.py#CartStore.get]
The not-found handler turns it into a 404 with `error` set to `not_found`. [src/cart/errors.py#_not_found_handler]
