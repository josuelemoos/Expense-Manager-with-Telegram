from calendar import monthrange
from datetime import date
from decimal import Decimal
from typing import Literal

from sqlmodel import Session, select

from app.models import Transaction
from app.schemas.budget import BudgetProgress
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionResult
from app.services.account_service import get_account_or_default
from app.services.budget_service import get_budget_progress
from app.services.category_service import (
    get_category_or_none,
    validate_category_for_transaction,
)
from app.services.exceptions import ValidationError
from app.utils.date_helpers import now_in_timezone


def _month_range(month: int, year: int) -> tuple[date, date]:
    if month < 1 or month > 12:
        raise ValidationError("Mes deve estar entre 1 e 12.")
    if year < 2000:
        raise ValidationError("Ano deve ser maior ou igual a 2000.")
    last_day = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def create_transaction(
    session: Session,
    user_id: int,
    data: TransactionCreate,
) -> Transaction:
    transaction, _, _ = _create_transaction_record(session, user_id, data)
    return transaction


def _create_transaction_record(
    session: Session,
    user_id: int,
    data: TransactionCreate,
) -> tuple[Transaction, Decimal, BudgetProgress | None]:
    account = get_account_or_default(session, user_id, data.account_id)
    category = get_category_or_none(session, user_id, data.category_id)
    validate_category_for_transaction(category, data.type)

    amount = data.amount.quantize(Decimal("0.01"))
    transaction = Transaction(
        user_id=user_id,
        account_id=account.id,
        category_id=category.id if category else None,
        type=data.type,
        amount=amount,
        description=data.description.strip(),
        date=data.date or now_in_timezone().date(),
        notes=data.notes,
        source=data.source,
    )

    if data.type == "income":
        account.current_balance += amount
    else:
        account.current_balance -= amount

    try:
        session.add(account)
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        session.refresh(account)
    except Exception:
        session.rollback()
        raise

    budget_progress = None
    if transaction.type == "expense" and transaction.category_id:
        budget_progress = get_budget_progress(
            session=session,
            user_id=user_id,
            category_id=transaction.category_id,
            month=transaction.date.month,
            year=transaction.date.year,
        )

    return transaction, account.current_balance, budget_progress


def create_transaction_with_result(
    session: Session,
    user_id: int,
    data: TransactionCreate,
) -> TransactionResult:
    transaction, account_balance, budget_progress = _create_transaction_record(
        session,
        user_id,
        data,
    )
    return TransactionResult(
        transaction=TransactionRead.model_validate(transaction),
        account_balance=account_balance,
        budget_progress=budget_progress,
    )


def create_expense(
    session: Session,
    user_id: int,
    data: TransactionCreate,
) -> TransactionResult:
    if data.type != "expense":
        raise ValidationError("Tipo da transacao deve ser expense.")
    return create_transaction_with_result(session, user_id, data)


def create_income(
    session: Session,
    user_id: int,
    data: TransactionCreate,
) -> TransactionResult:
    if data.type != "income":
        raise ValidationError("Tipo da transacao deve ser income.")
    return create_transaction_with_result(session, user_id, data)


def list_transactions(
    session: Session,
    user_id: int,
    month: int | None = None,
    year: int | None = None,
    type_: Literal["income", "expense", "transfer"] | None = None,
    category_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Transaction]:
    if (month is None) != (year is None):
        raise ValidationError("Informe month e year juntos para filtrar por periodo.")

    statement = select(Transaction).where(Transaction.user_id == user_id)
    if month is not None and year is not None:
        start_date, end_date = _month_range(month, year)
        statement = statement.where(
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        )
    if type_:
        statement = statement.where(Transaction.type == type_)
    if category_id:
        statement = statement.where(Transaction.category_id == category_id)

    return list(
        session.exec(
            statement.order_by(Transaction.date.desc(), Transaction.created_at.desc())
            .offset(offset)
            .limit(limit),
        ).all(),
    )


def list_recent_transactions(
    session: Session,
    user_id: int,
    limit: int = 5,
) -> list[Transaction]:
    return list(
        session.exec(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.date.desc(), Transaction.created_at.desc())
            .limit(limit),
        ).all(),
    )
