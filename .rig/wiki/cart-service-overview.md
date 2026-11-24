# Cart Service Overview

> High-level introduction to the cart package: what it does, how the modules fit together, and how a request flows from API to store.

## Modules

The `cart` package is a Python package marked by an empty `__init__` module. [src/cart/__init__.py]
The `main` module creates the FastAPI application titled "Shopping Cart API". [src/cart/main.py]
The `models` module holds the request and item models, and all validation rules live there. [src/cart/models.py]
The `store` module provides an in-memory, thread-safe cart. [src/cart/store.py#CartStore]
The `errors` module turns validation failures into 400 responses instead of 422. [src/cart/errors.py#register_error_handlers]

## API layer

The `main` module registers the error handlers on the application when it is imported. [src/cart/main.py]
A single module-level `CartStore` instance backs the endpoints. [src/cart/main.py]
`add_item` handles `POST /items` and returns status 201. [src/cart/main.py#add_item]
`add_item` takes an `ItemCreate` body and passes its name, price and quantity to the store's `add` method. [src/cart/main.py#add_item]
`list_items` handles `GET /items` and currently returns an empty list without reading the store. [src/cart/main.py#list_items]

## Models and validation

`ItemCreate` is the body of `POST /items`, and it ignores unknown fields. [src/cart/models.py#ItemCreate]
The `name` field must be a strict string, stripped of whitespace, with at least one character. [src/cart/models.py]
The `price` field is a `Decimal` of at least 0 with at most 2 decimal places, and it rejects infinity and NaN. [src/cart/models.py]
Before validation, the price field rejects strings and booleans because a price must be a JSON number. [src/cart/models.py#_reject_non_numbers]
The `quantity` field must be a strict integer of at least 1. [src/cart/models.py]
`Item` is a stored item with an `id`, `name`, `price` and `quantity`. [src/cart/models.py#Item]
`Item` serializes its price as a JSON number. [src/cart/models.py#Item]

## Store

`CartStore` holds items in insertion order, and one lock guards every access. [src/cart/store.py#CartStore]
`CartStore.add` generates a UUID4 string as the item id and builds an `Item`. [src/cart/store.py#CartStore.add]
`CartStore.add` appends the new item to the internal list while holding the lock, then returns it. [src/cart/store.py#CartStore.add]
`CartStore.list_all` returns a copy of the item list taken under the lock. [src/cart/store.py#CartStore.list_all]

## Error handling

`register_error_handlers` installs one handler for `RequestValidationError` and one for Starlette's `HTTPException`. [src/cart/errors.py#register_error_handlers]
Every validation error is returned with status 400 and a body containing `error` set to `validation_error` and a `message`. [src/cart/errors.py]
The message names the first invalid body field in the order name, price, quantity. [src/cart/errors.py]
Each field has a fixed message in a lookup table. [src/cart/errors.py]
When no known field is at fault, the message is "body must be a JSON object". [src/cart/errors.py]
When the errors do not come from the request body, the message names the last location element followed by "is invalid". [src/cart/errors.py]
The HTTP exception handler converts a 400 with the detail "There was an error parsing the body" into the same validation error body. [src/cart/errors.py]
The HTTP exception handler delegates all other HTTP exceptions to FastAPI's default handler. [src/cart/errors.py]

## Request flow

A valid `POST /items` request is validated against `ItemCreate`, added to the store, and returned as an `Item` with status 201. [src/cart/main.py#add_item]
An invalid request never reaches `add_item`, and the registered handler returns a 400 response instead. [src/cart/errors.py#register_error_handlers]

```mermaid
flowchart LR
    Client[Client POST /items] --> Validate[ItemCreate validation] %% [src/cart/models.py#ItemCreate]
    Validate -- invalid --> Handler[400 validation_error] %% [src/cart/errors.py#register_error_handlers]
    Validate -- valid --> Endpoint[add_item] %% [src/cart/main.py#add_item]
    Endpoint --> Add[CartStore.add] %% [src/cart/store.py#CartStore.add]
    Add --> Item[Item returned with 201] %% [src/cart/models.py#Item]
```
