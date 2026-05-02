from datetime import date
from decimal import Decimal

from sqlmodel import Session

from app.schemas.transaction import TransactionCreate
from app.services.transaction_service import create_expense, create_income

USER_ID = 1


def test_create_expense_updates_balance(session: Session, basic_data: dict[str, object]) -> None:
    account = basic_data["account"]
    food = basic_data["food"]

    result = create_expense(
        session,
        USER_ID,
        TransactionCreate(
            type="expense",
            amount=Decimal("45.00"),
            description="Mercado",
            category_id=food.id,
            date=date(2026, 5, 2),
        ),
    )

    session.refresh(account)
    assert account.current_balance == Decimal("955.00")
    assert result.transaction.amount == Decimal("45.00")
    assert result.account_balance == Decimal("955.00")


def test_create_income_updates_balance(session: Session, basic_data: dict[str, object]) -> None:
    account = basic_data["account"]
    salary = basic_data["salary"]

    result = create_income(
        session,
        USER_ID,
        TransactionCreate(
            type="income",
            amount=Decimal("1500.00"),
            description="Salario",
            category_id=salary.id,
            date=date(2026, 5, 2),
        ),
    )

    session.refresh(account)
    assert account.current_balance == Decimal("2500.00")
    assert result.transaction.amount == Decimal("1500.00")
    assert result.account_balance == Decimal("2500.00")
