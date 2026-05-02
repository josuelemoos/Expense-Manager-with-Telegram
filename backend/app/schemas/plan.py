from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, computed_field


class MonthlyPlanUpsert(BaseModel):
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000)
    expected_income: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    committed_expenses: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    notes: str | None = None


class MonthlyPlanRead(BaseModel):
    id: int | None = None
    user_id: int
    month: int
    year: int
    expected_income: Decimal
    committed_expenses: Decimal
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    warning: str | None = None

    @computed_field
    @property
    def free_amount(self) -> Decimal:
        return (self.expected_income - self.committed_expenses).quantize(Decimal("0.01"))

    model_config = ConfigDict(from_attributes=True)


class AllocationRuleUpsert(BaseModel):
    id: int | None = None
    name: str = Field(min_length=1, max_length=100)
    percentage: Decimal = Field(ge=0, le=100, max_digits=5, decimal_places=2)
    category_id: int | None = None
    emoji: str | None = Field(default=None, max_length=10)
    sort_order: int = 0
    is_active: bool = True


class AllocationRuleRead(BaseModel):
    id: int
    user_id: int
    name: str
    percentage: Decimal
    category_id: int | None
    emoji: str | None
    sort_order: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class AllocationProgress(BaseModel):
    rule_id: int
    name: str
    percentage: Decimal
    planned_amount: Decimal
    spent_amount: Decimal
    used_percentage: Decimal
    category_id: int | None = None
    emoji: str | None = None
    is_over: bool = False
    alert_message: str | None = None


class PlanProgress(BaseModel):
    plan: MonthlyPlanRead
    allocations: list[AllocationProgress]
    unallocated_percentage: Decimal
    unallocated_amount: Decimal
