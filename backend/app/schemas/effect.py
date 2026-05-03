from datetime import date as PyDate
from decimal import Decimal

from pydantic import BaseModel, Field


class BudgetEffect(BaseModel):
    category_id: int
    category_name: str
    limit_value: Decimal
    current_spent: Decimal
    projected_spent: Decimal
    current_percentage: Decimal
    projected_percentage: Decimal
    alert_message: str | None = None


class AllocationEffect(BaseModel):
    rule_id: int
    name: str
    planned_amount: Decimal
    current_spent: Decimal
    projected_spent: Decimal
    current_percentage: Decimal
    projected_percentage: Decimal
    emoji: str | None = None
    alert_message: str | None = None


class ExpenseEffectSimulation(BaseModel):
    description: str
    amount: Decimal
    date: PyDate
    category_id: int | None = None
    category_name: str
    current_account_balance: Decimal
    projected_account_balance: Decimal
    current_monthly_balance: Decimal
    projected_monthly_balance: Decimal
    current_plan_remaining: Decimal
    projected_plan_remaining: Decimal
    budget: BudgetEffect | None = None
    allocation: AllocationEffect | None = None
    alerts: list[str] = Field(default_factory=list)
