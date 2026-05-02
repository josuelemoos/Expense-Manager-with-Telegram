from decimal import Decimal

from pydantic import BaseModel

from app.schemas.account import AccountBalanceItem
from app.schemas.transaction import TransactionRead


class CategorySpending(BaseModel):
    category_id: int | None
    category_name: str
    total: Decimal
    percentage: Decimal


class MonthlySummary(BaseModel):
    month: int
    year: int
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    expenses_by_category: list[CategorySpending]
    top_expenses: list[CategorySpending]


class DashboardSummary(BaseModel):
    month: int
    year: int
    total_income: Decimal
    total_expense: Decimal
    monthly_balance: Decimal
    total_reserved: Decimal
    total_account_balance: Decimal
    accounts: list[AccountBalanceItem]
    recent_transactions: list[TransactionRead]
