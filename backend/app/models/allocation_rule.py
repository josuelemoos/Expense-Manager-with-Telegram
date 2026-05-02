from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, Numeric, String, text
from sqlmodel import Field, SQLModel


class AllocationRule(SQLModel, table=True):
    __tablename__ = "allocation_rules"
    __table_args__ = (
        CheckConstraint(
            "percentage >= 0 AND percentage <= 100",
            name="ck_allocation_rules_percentage_range",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    )
    name: str = Field(sa_column=Column(String(100), nullable=False))
    percentage: Decimal = Field(sa_column=Column(Numeric(5, 2), nullable=False))
    category_id: int | None = Field(
        default=None,
        sa_column=Column(ForeignKey("categories.id"), nullable=True),
    )
    emoji: str | None = Field(default=None, sa_column=Column(String(10), nullable=True))
    sort_order: int = Field(
        default=0,
        sa_column=Column(Integer, nullable=False, server_default=text("0")),
    )
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
    )
