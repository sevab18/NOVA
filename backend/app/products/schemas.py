##проверка данных через Pydantic 
from decimal import Decimal

from pydantic import BaseModel,ConfigDict, Field

class ProductCreate(BaseModel):
    name: str= Field(min_length=1, max_length=200)
    description: str | None = Field(
        default=None,
        max_length=1000

    )
    price: Decimal= Field (
        ge=0,
        max_digits=12,
        decimal_places=2
    )

    stock: int = Field(
        default=0,
        ge=0
    )
    category_id: int | None = Field(
        default=None,
        gt=0,
    )

class ProductResponse(ProductCreate):
    model_config=ConfigDict(from_attributes=True)

    id: int



