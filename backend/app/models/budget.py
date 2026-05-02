from decimal import Decimal

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlmodel import Field, SQLModel


class Budget(SQLModel, table=True):
    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint("user_id", "category_id", "month", "year", name="uq_budgets_user_category_month_year"),
        CheckConstraint("month BETWEEN 1 AND 12", name="ck_budgets_month"),
        CheckConstraint("year >= 2000", name="ck_budgets_year"),
        CheckConstraint("limit_value >= 0", name="ck_budgets_limit_non_negative"),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    )
    category_id: int = Field(
        sa_column=Column(ForeignKey("categories.id"), nullable=False),
    )
    month: int = Field(sa_column=Column(Integer, nullable=False))
    year: int = Field(sa_column=Column(Integer, nullable=False))
    limit_value: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
