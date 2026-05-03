from datetime import date
from decimal import Decimal

import pytest
from sqlmodel import Session, select

from app.models import Account, AllocationRule, Category, Reserve, Transaction
from app.schemas.transaction import TransactionCreate
from app.services.reset_service import reset_financial_data
from app.services.transaction_service import create_expense
from app.telegram.reset_state import (
    clear_pending_resets,
    consume_pending_reset,
    create_pending_reset,
)

USER_ID = 1


def test_reset_requires_confirmation(
    session: Session,
    basic_data: dict[str, object],
) -> None:
    account = basic_data["account"]
    food = basic_data["food"]
    create_expense(
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

    pending = create_pending_reset(chat_id=123, user_id=USER_ID, initial_balance=Decimal("5000.00"))

    session.refresh(account)
    transactions = session.exec(select(Transaction)).all()
    assert pending.confirmation_code
    assert account.current_balance == Decimal("955.00")
    assert len(transactions) == 1
    clear_pending_resets()


def test_reset_recreates_seed_with_balance(
    session: Session,
    basic_data: dict[str, object],
) -> None:
    food = basic_data["food"]
    create_expense(
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

    result = reset_financial_data(
        session,
        USER_ID,
        initial_balance=Decimal("5000.00"),
    )

    accounts = session.exec(select(Account).order_by(Account.name)).all()
    categories = session.exec(select(Category)).all()
    reserves = session.exec(select(Reserve)).all()
    rules = session.exec(select(AllocationRule)).all()
    transactions = session.exec(select(Transaction)).all()
    default_account = next(account for account in accounts if account.is_default)

    assert result.initial_balance == Decimal("5000.00")
    assert result.deleted_transactions == 1
    assert transactions == []
    assert default_account.name == "Conta Principal"
    assert default_account.initial_balance == Decimal("5000.00")
    assert default_account.current_balance == Decimal("5000.00")
    assert len(accounts) == 2
    assert len(categories) >= 10
    assert len(reserves) == 3
    assert len(rules) == 4


def test_reset_confirmation_consumed_once() -> None:
    clear_pending_resets()
    pending = create_pending_reset(chat_id=123, user_id=USER_ID, initial_balance=Decimal("0.00"))

    assert consume_pending_reset(123, pending.confirmation_code) == pending
    assert consume_pending_reset(123, pending.confirmation_code) is None


def test_reset_rolls_back_on_failure(
    monkeypatch: pytest.MonkeyPatch,
    session: Session,
    basic_data: dict[str, object],
) -> None:
    food = basic_data["food"]
    create_expense(
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

    def fail_commit() -> None:
        raise RuntimeError("database failed")

    monkeypatch.setattr(session, "commit", fail_commit)

    with pytest.raises(RuntimeError):
        reset_financial_data(
            session,
            USER_ID,
            initial_balance=Decimal("5000.00"),
        )

    transactions = session.exec(select(Transaction)).all()
    accounts = session.exec(select(Account)).all()
    assert len(transactions) == 1
    assert any(account.current_balance == Decimal("955.00") for account in accounts)
