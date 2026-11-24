# Domain Models

> Data models for carts and items: fields, validation rules, and how they are used across the service.

## Overview

All validation rules for requests and items live in one module. [src/cart/models.py]
The module defines two Pydantic models, `ItemCreate` and `Item`. [src/cart/models.py#ItemCreate]
`ItemCreate` is the request body and `Item` is the stored representation. [src/cart/models.py#Item]

## ItemCreate

`ItemCreate` is the body of `POST /items`. [src/cart/models.py#ItemCreate]
Unknown fields are ignored rather than rejected, because the model config sets `extra="ignore"`. [src/cart/models.py#ItemCreate]
It has three fields: `name`, `price` and `quantity`. [src/cart/models.py#ItemCreate]

### name

The `name` field uses a string type with strict typing, so other types are not coerced to strings. [src/cart/models.py#ItemCreate]
Leading and trailing whitespace is stripped from `name`. [src/cart/models.py#ItemCreate]
After stripping, `name` must be at least one character long. [src/cart/models.py#ItemCreate]

### price

The `price` field is a `Decimal`. [src/cart/models.py#ItemCreate]
A `price` must be greater than or equal to zero. [src/cart/models.py#ItemCreate]
A `price` may have at most two decimal places. [src/cart/models.py#ItemCreate]
Infinity and NaN are not allowed for `price`. [src/cart/models.py#ItemCreate]
Before the other checks run, `_reject_non_numbers` rejects any string or boolean value. [src/cart/models.py#_reject_non_numbers]
The rejection raises a custom error with code `price_type` and the message "price must be a number". [src/cart/models.py#_reject_non_numbers]

### quantity

The `quantity` field is an integer with strict typing, so values such as strings are not coerced. [src/cart/models.py#ItemCreate]
A `quantity` must be greater than or equal to one. [src/cart/models.py#ItemCreate]

## Item

`Item` is a stored item with the fields `id`, `name`, `price` and `quantity`. [src/cart/models.py#Item]
The `id` and `name` fields are plain strings. [src/cart/models.py#Item]
The `quantity` field is a plain integer. [src/cart/models.py#Item]
The `price` field is a `Decimal` in Python. [src/cart/models.py#Item]
When serialized to JSON, `price` is converted to a float by a `PlainSerializer`. [src/cart/models.py#Item]
The serializer applies only in JSON mode, because it is set with `when_used="json"`. [src/cart/models.py#Item]
`Item` does not repeat the `ItemCreate` validation constraints. [src/cart/models.py#Item]

## Model relationships

```mermaid
flowchart LR
    A[Request body] -->|validated by| B[ItemCreate] %% [src/cart/models.py#ItemCreate]
    B --> C[name: strict, stripped, min length 1] %% [src/cart/models.py#ItemCreate]
    B --> D[price: Decimal, >= 0, 2 places] %% [src/cart/models.py#ItemCreate]
    B --> E[quantity: strict int, >= 1] %% [src/cart/models.py#ItemCreate]
    D -->|pre-check| F[_reject_non_numbers] %% [src/cart/models.py#_reject_non_numbers]
    G[Item] -->|price as JSON number| H[Response] %% [src/cart/models.py#Item]
```
