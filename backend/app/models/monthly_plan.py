from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, Numeric, Text, UniqueConstraint, text
from sqlmodel import Field, SQLModel


class MonthlyPlan(SQLModel, table=True):
    __tablename__ = "monthly_plans"
    __table_args__ = (
        UniqueConstraint("user_id", "month", "year", name="uq_monthly_plans_user_month_year"),
        CheckConstraint("month BETWEEN 1 AND 12", name="ck_monthly_plans_month"),
        CheckConstraint("year >= 2000", name="ck_monthly_plans_year"),
        CheckConstraint("expected_income >= 0", name="ck_monthly_plans_expected_non_negative"),
        CheckConstraint("committed_expenses >= 0", name="ck_monthly_plans_committed_non_negative"),
        CheckConstraint(
            "committed_expenses <= expected_income",
            name="ck_monthly_plans_committed_lte_expected",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    )
    month: int = Field(sa_column=Column(Integer, nullable=False))
    year: int = Field(sa_column=Column(Integer, nullable=False))
    expected_income: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    committed_expenses: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    notes: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime, nullable=False, server_default=text("now()")),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime, nullable=False, server_default=text("now()")),
    )
