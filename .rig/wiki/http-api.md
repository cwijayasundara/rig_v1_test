# HTTP API

> The application entry point and its endpoints: routing, request/response handling, and how errors are surfaced to clients.

## Application

The module `src/cart/main.py` creates a FastAPI application titled "Shopping Cart API". [src/cart/main.py]
The module calls `register_error_handlers` on the application at import time. [src/cart/main.py]
The module creates a single `CartStore` instance at module level, and the handlers share it. [src/cart/main.py]
The package `src/cart/__init__.py` is an empty file. [src/cart/__init__.py]

## Endpoints

### POST /items

The `add_item` handler is registered for `POST /items` with status code 201. [src/cart/main.py#add_item]
It accepts a request body validated as `ItemCreate`. [src/cart/main.py#add_item]
It calls `add` on the shared store with the body's `name`, `price` and `quantity`. [src/cart/main.py#add_item]
It returns the `Item` produced by the store. [src/cart/main.py#add_item]

### GET /items

The `list_items` handler is registered for `GET /items`. [src/cart/main.py#list_items]
It takes no parameters. [src/cart/main.py#list_items]
It always returns an empty list. [src/cart/main.py#list_items]
It does not read from the store. [src/cart/main.py#list_items]
Items added through `POST /items` therefore do not appear in its response. [src/cart/main.py#list_items]

## Error handling

The application gets its error handlers from `register_error_handlers`, imported from `cart.errors`. [src/cart/main.py]
This page does not describe what those handlers do, because `cart.errors` is not among the supplied sources. [src/cart/main.py]

## Request flow

```mermaid
flowchart LR %% [src/cart/main.py]
    Client[Client] -->|POST /items| AddItem[add_item] %% [src/cart/main.py#add_item]
    AddItem -->|name, price, quantity| Store[CartStore.add] %% [src/cart/main.py#add_item]
    Store -->|Item, 201| Client %% [src/cart/main.py#add_item]
    Client2[Client] -->|GET /items| ListItems[list_items] %% [src/cart/main.py#list_items]
    ListItems -->|empty list| Client2 %% [src/cart/main.py#list_items]
```
