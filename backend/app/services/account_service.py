from decimal import Decimal

from sqlmodel import Session, select

from app.models import Account
from app.services.exceptions import NotFoundError


def list_accounts(session: Session, user_id: int) -> list[Account]:
    return list(
        session.exec(
            select(Account)
            .where(Account.user_id == user_id, Account.is_active == True)
            .order_by(Account.is_default.desc(), Account.name),
        ).all(),
    )


def get_account(session: Session, user_id: int, account_id: int) -> Account:
    account = session.exec(
        select(Account).where(
            Account.id == account_id,
            Account.user_id == user_id,
            Account.is_active == True,
        ),
    ).first()
    if not account:
        raise NotFoundError("Conta nao encontrada.")
    return account


def get_default_account(session: Session, user_id: int) -> Account:
    account = session.exec(
        select(Account).where(
            Account.user_id == user_id,
            Account.is_active == True,
            Account.is_default == True,
        ),
    ).first()
    if account:
        return account

    account = session.exec(
        select(Account).where(
            Account.user_id == user_id,
            Account.is_active == True,
        ),
    ).first()
    if not account:
        raise NotFoundError("Nenhuma conta ativa encontrada para o usuario.")
    return account


def get_account_or_default(
    session: Session,
    user_id: int,
    account_id: int | None,
) -> Account:
    if account_id is None:
        return get_default_account(session, user_id)
    return get_account(session, user_id, account_id)


def total_balance(accounts: list[Account]) -> Decimal:
    return sum((account.current_balance for account in accounts), Decimal("0.00"))
