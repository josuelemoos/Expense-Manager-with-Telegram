from functools import lru_cache
from decimal import Decimal
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+psycopg://fintrack:fintrack@localhost:5432/fintrack",
        validation_alias="DATABASE_URL",
    )
    database_echo: bool = Field(default=False, validation_alias="DATABASE_ECHO")

    secret_key: str = Field(default="change-me", validation_alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", validation_alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=60,
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    telegram_bot_token: str | None = Field(
        default=None,
        validation_alias="TELEGRAM_BOT_TOKEN",
    )
    telegram_webhook_url: str | None = Field(
        default=None,
        validation_alias="TELEGRAM_WEBHOOK_URL",
    )

    default_user_id: int = Field(default=1, validation_alias="DEFAULT_USER_ID")
    default_user_telegram_chat_id: int | None = Field(
        default=None,
        validation_alias="DEFAULT_USER_TELEGRAM_CHAT_ID",
    )
    default_monthly_income: Decimal = Field(
        default=Decimal("3000.00"),
        validation_alias="DEFAULT_MONTHLY_INCOME",
    )
    timezone: str = Field(default="America/Fortaleza", validation_alias="TIMEZONE")

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator(
        "telegram_bot_token",
        "telegram_webhook_url",
        "default_user_telegram_chat_id",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value: object) -> object:
        if value == "":
            return None
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
