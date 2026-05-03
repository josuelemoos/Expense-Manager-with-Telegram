from datetime import date as Date
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.budget import BudgetProgress


class TransactionCreate(BaseModel):
    account_id: int | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)
    type: Literal["income", "expense"]
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    description: str = Field(min_length=1, max_length=255)
    date: Date | None = None
    notes: str | None = Field(default=None, max_length=1000)
    source: Literal["manual", "telegram", "import"] = "manual"

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Descricao nao pode ficar vazia.")
        return value

    @field_validator("notes", mode="before")
    @classmethod
    def blank_notes_to_none(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class TransactionRead(BaseModel):
    id: int
    user_id: int
    account_id: int | None
    category_id: int | None
    type: Literal["income", "expense", "transfer"]
    amount: Decimal
    description: str
    date: Date
    notes: str | None
    source: Literal["manual", "telegram", "import"]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionResult(BaseModel):
    transaction: TransactionRead
    account_balance: Decimal
    budget_progress: BudgetProgress | None = None
