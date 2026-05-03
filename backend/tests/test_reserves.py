from decimal import Decimal

import pytest
from sqlmodel import Session, select

from app.models import Transaction
from app.schemas.reserve import ReserveDepositCreate
from app.services.exceptions import ValidationError
from app.services.reserve_service import deposit_to_reserve

USER_ID = 1


def test_reserve_deposit_updates_both(session: Session, basic_data: dict[str, object]) -> None:
    account = basic_data["account"]
    reserve = basic_data["reserve"]

    updated_reserve, account_balance, progress = deposit_to_reserve(
        session,
        USER_ID,
        reserve.id,
        ReserveDepositCreate(amount=Decimal("200.00")),
    )

    session.refresh(account)
    assert account.current_balance == Decimal("800.00")
    assert updated_reserve.current_value == Decimal("200.00")
    assert account_balance == Decimal("800.00")
    assert progress == Decimal("3.33")


def test_reserve_deposit_fails_if_no_balance(
    session: Session,
    basic_data: dict[str, object],
) -> None:
    account = basic_data["account"]
    reserve = basic_data["reserve"]

    with pytest.raises(ValidationError):
        deposit_to_reserve(
            session,
            USER_ID,
            reserve.id,
            ReserveDepositCreate(amount=Decimal("2000.00")),
        )

    session.refresh(account)
    session.refresh(reserve)
    assert account.current_balance == Decimal("1000.00")
    assert reserve.current_value == Decimal("0.00")


def test_reserve_deposit_rolls_back_if_commit_fails(
    monkeypatch: pytest.MonkeyPatch,
    session: Session,
    basic_data: dict[str, object],
) -> None:
    account = basic_data["account"]
    reserve = basic_data["reserve"]

    def fail_commit() -> None:
        raise RuntimeError("database failed")

    monkeypatch.setattr(session, "commit", fail_commit)

    with pytest.raises(RuntimeError):
        deposit_to_reserve(
            session,
            USER_ID,
            reserve.id,
            ReserveDepositCreate(amount=Decimal("200.00")),
        )

    session.refresh(account)
    session.refresh(reserve)
    transactions = session.exec(select(Transaction)).all()
    assert account.current_balance == Decimal("1000.00")
    assert reserve.current_value == Decimal("0.00")
    assert transactions == []
