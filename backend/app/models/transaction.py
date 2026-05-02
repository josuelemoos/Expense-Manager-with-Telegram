from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Column, Date, DateTime, ForeignKey, Numeric, String, Text, func, text
from sqlmodel import Field, SQLModel


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint(
            "type IN ('income', 'expense', 'transfer')",
            name="ck_transactions_type",
        ),
        CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        CheckConstraint(
            "source IN ('manual', 'telegram', 'import')",
            name="ck_transactions_source",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    )
    account_id: int | None = Field(
        default=None,
        sa_column=Column(ForeignKey("accounts.id"), nullable=True),
    )
    category_id: int | None = Field(
        default=None,
        sa_column=Column(ForeignKey("categories.id"), nullable=True),
    )
    type: str = Field(sa_column=Column(String(15), nullable=False))
    amount: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    description: str = Field(sa_column=Column(String(255), nullable=False))
    date: date | None = Field(
        default=None,
        sa_column=Column(Date, nullable=False, server_default=text("CURRENT_DATE")),
    )
    notes: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    source: str = Field(
        default="manual",
        sa_column=Column(
            String(20),
            nullable=False,
            server_default=text("'manual'"),
        ),
    )
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime, nullable=False, server_default=func.now()),
    )
