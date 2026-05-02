from decimal import Decimal

from pydantic import BaseModel


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
