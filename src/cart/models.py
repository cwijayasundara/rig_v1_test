"""Request and item models; all validation rules live here."""

from decimal import Decimal
from typing import Annotated, Any

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
    StringConstraints,
)
from pydantic_core import PydanticCustomError


def _reject_non_numbers(value: Any) -> Any:
    """A price must be a JSON number: strings and booleans are not numbers."""
    if isinstance(value, (str, bool)):
        raise PydanticCustomError("price_type", "price must be a number")
    return value


_Name = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1)]
_Price = Annotated[
    Decimal,
    BeforeValidator(_reject_non_numbers),
    Field(ge=0, decimal_places=2, allow_inf_nan=False),
]
_Quantity = Annotated[int, Field(strict=True, ge=1)]


class ItemCreate(BaseModel):
    """Body of POST /items; unknown fields are ignored."""

    model_config = ConfigDict(extra="ignore")

    name: _Name
    price: _Price
    quantity: _Quantity


class Item(BaseModel):
    """A stored item; price leaves as a JSON number."""

    id: str
    name: str
    price: Annotated[
        Decimal, PlainSerializer(lambda value: float(value), return_type=float, when_used="json")
    ]
    quantity: int
