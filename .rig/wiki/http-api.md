# HTTP API

> The application entry point and its endpoints: routing, request/response handling, and how errors are surfaced to clients.

## Application setup

The module `cart.main` creates a FastAPI application titled "Shopping Cart API". [src/cart/main.py]
The module calls `register_error_handlers` with the application right after creating it. [src/cart/main.py]
A single module-level `CartStore` instance named `store` is shared by all request handlers. [src/cart/main.py]

## Endpoints

`add_item` handles `POST /items`. [src/cart/main.py#add_item]
`list_items` handles `GET /items`. [src/cart/main.py#list_items]
`get_item` handles `GET /items/{item_id}`. [src/cart/main.py#get_item]

### POST /items

`add_item` accepts a request body validated as `ItemCreate`. [src/cart/main.py#add_item]
`add_item` responds with HTTP status 201. [src/cart/main.py#add_item]
`add_item` passes the body's name, price and quantity to `store.add`. [src/cart/main.py#add_item]
`add_item` returns the `Item` produced by `store.add`. [src/cart/main.py#add_item]

### GET /items

`list_items` is declared to return a list of dictionaries mapping strings to objects. [src/cart/main.py#list_items]
`list_items` currently returns an empty list without reading the store. [src/cart/main.py#list_items]

### GET /items/{item_id}

`get_item` takes `item_id` from the path as a string. [src/cart/main.py#get_item]
`get_item` returns the `Item` produced by `store.get` for that identifier. [src/cart/main.py#get_item]

## Error handling

Error responses are configured by `register_error_handlers`, which is invoked once at import time. [src/cart/main.py]

## Request flow

```mermaid
flowchart LR
    Client[Client] --> App[FastAPI app] %% [src/cart/main.py]
    App --> Add[add_item POST /items] %% [src/cart/main.py#add_item]
    App --> List[list_items GET /items] %% [src/cart/main.py#list_items]
    App --> Get[get_item GET /items/item_id] %% [src/cart/main.py#get_item]
    Add --> Store[(CartStore store)] %% [src/cart/main.py]
    Get --> Store %% [src/cart/main.py]
```
