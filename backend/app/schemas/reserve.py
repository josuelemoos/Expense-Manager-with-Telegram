from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReserveCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    goal_value: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    description: str | None = Field(default=None, max_length=1000)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Nome da reserva nao pode ficar vazio.")
        return value

    @field_validator("description", mode="before")
    @classmethod
    def blank_description_to_none(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ReserveDepositCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    account_id: int | None = Field(default=None, gt=0)
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("notes", mode="before")
    @classmethod
    def blank_notes_to_none(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


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
