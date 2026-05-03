from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class PendingReset(BaseModel):
    chat_id: int
    user_id: int
    confirmation_code: str
    initial_balance: Decimal
    expires_at: datetime


class ResetResult(BaseModel):
    user_id: int
    initial_balance: Decimal
    deleted_transactions: int
    deleted_accounts: int
    deleted_categories: int
    deleted_reserves: int
    deleted_budgets: int
    deleted_monthly_plans: int
    deleted_allocation_rules: int
