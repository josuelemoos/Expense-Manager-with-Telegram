from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BudgetUpsert(BaseModel):
    category_id: int
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000)
    limit_value: Decimal = Field(ge=0, max_digits=12, decimal_places=2)


class BudgetRead(BaseModel):
    id: int
    user_id: int
    category_id: int
    month: int
    year: int
    limit_value: Decimal

    model_config = ConfigDict(from_attributes=True)


class BudgetProgress(BaseModel):
    category_id: int
    category_name: str
    month: int
    year: int
    limit_value: Decimal
    spent_value: Decimal
    percentage_used: Decimal
    alert_level: str | None = None
    alert_message: str | None = None
