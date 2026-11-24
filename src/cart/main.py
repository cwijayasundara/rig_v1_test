from fastapi import FastAPI

app = FastAPI(title="Shopping Cart API")


@app.get("/items")
def list_items() -> list[dict[str, object]]:
    return []
