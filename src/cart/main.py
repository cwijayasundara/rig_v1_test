from fastapi import FastAPI

from cart.errors import register_error_handlers
from cart.models import Item, ItemCreate
from cart.store import CartStore

app = FastAPI(title="Shopping Cart API")
register_error_handlers(app)

store = CartStore()


@app.post("/items", status_code=201)
def add_item(body: ItemCreate) -> Item:
    return store.add(body.name, body.price, body.quantity)


@app.get("/items")
def list_items() -> list[dict[str, object]]:
    return []


@app.get("/items/{item_id}")
def get_item(item_id: str) -> Item:
    return store.get(item_id)
