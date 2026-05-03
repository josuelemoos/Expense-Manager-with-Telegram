from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class MonthlyPlanUpsert(BaseModel):
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000)
    expected_income: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    committed_expenses: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("notes", mode="before")
    @classmethod
    def blank_notes_to_none(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


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
    id: int | None = Field(default=None, gt=0)
    name: str = Field(min_length=1, max_length=100)
    percentage: Decimal = Field(ge=0, le=100, max_digits=5, decimal_places=2)
    category_id: int | None = Field(default=None, gt=0)
    emoji: str | None = Field(default=None, max_length=10)
    sort_order: int = Field(default=0, ge=0)
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Nome da alocacao nao pode ficar vazio.")
        return value

    @field_validator("emoji", mode="before")
    @classmethod
    def blank_emoji_to_none(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


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
