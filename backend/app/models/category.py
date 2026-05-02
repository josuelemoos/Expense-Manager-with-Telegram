from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Numeric, String, text
from sqlmodel import Field, SQLModel


class Category(SQLModel, table=True):
    __tablename__ = "categories"
    __table_args__ = (
        CheckConstraint(
            "type IN ('expense', 'income')",
            name="ck_categories_type",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    )
    name: str = Field(sa_column=Column(String(100), nullable=False))
    type: str = Field(sa_column=Column(String(10), nullable=False))
    monthly_limit: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(12, 2), nullable=True),
    )
    color: str | None = Field(default=None, sa_column=Column(String(7), nullable=True))
    icon: str | None = Field(default=None, sa_column=Column(String(50), nullable=True))
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
    )
