from decimal import Decimal

from sqlalchemy import delete
from sqlmodel import Session

from app.config import settings
from app.models import (
    Account,
    AllocationRule,
    Budget,
    Category,
    MonthlyPlan,
    Reserve,
    Transaction,
)
from app.schemas.reset import ResetResult
from app.seed import (
    get_or_create_user,
    money,
    seed_accounts,
    seed_allocation_rules,
    seed_categories,
    seed_reserves,
    sync_postgres_sequences,
)
from app.services.atomic import atomic_write
from app.services.exceptions import ValidationError


def validate_reset_balance(value: Decimal | None) -> Decimal:
    balance = money(value or "0")
    if balance < 0:
        raise ValidationError("Saldo inicial do reset nao pode ser negativo.")
    if balance > settings.reset_max_balance:
        raise ValidationError(
            f"Saldo inicial do reset nao pode passar de {money(settings.reset_max_balance)}.",
        )
    return balance


def _delete_for_user(session: Session, model: type, user_id: int) -> int:
    result = session.exec(delete(model).where(model.user_id == user_id))
    return int(result.rowcount or 0)


def reset_financial_data(
    session: Session,
    user_id: int,
    initial_balance: Decimal | None = None,
) -> ResetResult:
    if user_id != settings.default_user_id:
        raise ValidationError("Reset disponivel apenas para o usuario padrao do MVP.")

    balance = validate_reset_balance(initial_balance)
    with atomic_write(session):
        user = get_or_create_user(session)
        if user.id != user_id:
            raise ValidationError("Usuario padrao inconsistente para reset.")

        deleted_transactions = _delete_for_user(session, Transaction, user_id)
        deleted_budgets = _delete_for_user(session, Budget, user_id)
        deleted_monthly_plans = _delete_for_user(session, MonthlyPlan, user_id)
        deleted_allocation_rules = _delete_for_user(session, AllocationRule, user_id)
        deleted_reserves = _delete_for_user(session, Reserve, user_id)
        deleted_accounts = _delete_for_user(session, Account, user_id)
        deleted_categories = _delete_for_user(session, Category, user_id)

        session.flush()
        session.expunge_all()

        seed_accounts(session, user_id, default_initial_balance=balance)
        categories = seed_categories(session, user_id)
        seed_reserves(session, user_id)
        seed_allocation_rules(session, user_id, categories)
        sync_postgres_sequences(session)

    return ResetResult(
        user_id=user_id,
        initial_balance=balance,
        deleted_transactions=deleted_transactions,
        deleted_accounts=deleted_accounts,
        deleted_categories=deleted_categories,
        deleted_reserves=deleted_reserves,
        deleted_budgets=deleted_budgets,
        deleted_monthly_plans=deleted_monthly_plans,
        deleted_allocation_rules=deleted_allocation_rules,
    )
