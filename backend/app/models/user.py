from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, text
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(100), nullable=False))
    email: str = Field(sa_column=Column(String(150), nullable=False, unique=True))
    password_hash: str = Field(sa_column=Column(String(255), nullable=False))
    telegram_chat_id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, unique=True, nullable=True),
    )
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("now()"),
        ),
    )
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
    )
