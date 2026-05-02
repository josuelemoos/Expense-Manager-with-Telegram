from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ReserveCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    goal_value: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    description: str | None = None


class ReserveDepositCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    account_id: int | None = None
    notes: str | None = None


class ReserveRead(BaseModel):
    id: int
    user_id: int
    name: str
    current_value: Decimal
    goal_value: Decimal | None
    description: str | None
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ReserveDepositRead(BaseModel):
    reserve: ReserveRead
    account_balance: Decimal
    progress_percentage: Decimal | None
