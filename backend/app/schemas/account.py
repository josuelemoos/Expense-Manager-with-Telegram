from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AccountRead(BaseModel):
    id: int
    name: str
    type: Literal["wallet", "bank", "savings", "credit"]
    initial_balance: Decimal
    current_balance: Decimal
    created_at: datetime
    is_active: bool
    is_default: bool

    model_config = ConfigDict(from_attributes=True)


class AccountBalanceItem(BaseModel):
    id: int
    name: str
    type: Literal["wallet", "bank", "savings", "credit"]
    current_balance: Decimal
    is_default: bool

    model_config = ConfigDict(from_attributes=True)


class AccountBalanceSummary(BaseModel):
    total: Decimal = Field(default=Decimal("0.00"))
    accounts: list[AccountBalanceItem]
