from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Numeric, String, Text, text
from sqlmodel import Field, SQLModel


class Reserve(SQLModel, table=True):
    __tablename__ = "reserves"
    __table_args__ = (
        CheckConstraint("current_value >= 0", name="ck_reserves_current_non_negative"),
        CheckConstraint("goal_value IS NULL OR goal_value >= 0", name="ck_reserves_goal_non_negative"),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    )
    name: str = Field(sa_column=Column(String(100), nullable=False))
    current_value: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(
            Numeric(12, 2),
            nullable=False,
            server_default=text("0"),
        ),
    )
    goal_value: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(12, 2), nullable=True),
    )
    description: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime, nullable=False, server_default=text("now()")),
    )
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
    )
