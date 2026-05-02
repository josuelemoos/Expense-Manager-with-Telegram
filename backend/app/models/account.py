from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Numeric, String, func, text
from sqlmodel import Field, SQLModel


class Account(SQLModel, table=True):
    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint(
            "type IN ('wallet', 'bank', 'savings', 'credit')",
            name="ck_accounts_type",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    )
    name: str = Field(sa_column=Column(String(100), nullable=False))
    type: str = Field(sa_column=Column(String(30), nullable=False))
    initial_balance: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(
            Numeric(12, 2),
            nullable=False,
            server_default=text("0"),
        ),
    )
    current_balance: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(
            Numeric(12, 2),
            nullable=False,
            server_default=text("0"),
        ),
    )
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime, nullable=False, server_default=func.now()),
    )
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
    )
    is_default: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
    )
