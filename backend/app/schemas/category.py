from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict


class CategoryRead(BaseModel):
    id: int
    name: str
    type: Literal["expense", "income"]
    monthly_limit: Decimal | None
    color: str | None
    icon: str | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
