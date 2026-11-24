"""Error bodies and the validation-error handler (400, never 422)."""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException

_FIELD_MESSAGES = {
    "name": "name must be a non-empty string",
    "price": "price must be a number of at least 0 with at most 2 decimal places",
    "quantity": "quantity must be an integer of at least 1",
}
_BODY_MESSAGE = "body must be a JSON object"


def _error_response(message: str) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"error": "validation_error", "message": message},
    )


def _validation_message(errors: list[Any]) -> str:
    """Name the first invalid body field in the order name, price, quantity."""
    body_errors = [e["loc"] for e in errors if e["loc"][0] == "body"]
    if not body_errors and errors:
        return f"{errors[0]['loc'][-1]} is invalid"
    bad = {loc[1] for loc in body_errors if len(loc) > 1}
    for field, message in _FIELD_MESSAGES.items():
        if field in bad:
            return message
    return _BODY_MESSAGE


async def _validation_handler(request: Request, exc: Exception) -> Response:
    assert isinstance(exc, RequestValidationError)
    return _error_response(_validation_message(list(exc.errors())))


async def _http_handler(request: Request, exc: Exception) -> Response:
    assert isinstance(exc, StarletteHTTPException)
    if exc.status_code == 400 and exc.detail == "There was an error parsing the body":
        return _error_response(_BODY_MESSAGE)
    return await http_exception_handler(request, exc)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, _validation_handler)
    app.add_exception_handler(StarletteHTTPException, _http_handler)
