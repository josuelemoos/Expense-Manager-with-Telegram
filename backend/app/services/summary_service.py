from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Category, Reserve, Transaction
from app.schemas.account import AccountBalanceItem
from app.schemas.account import AccountBalanceSummary
from app.schemas.summary import CategorySpending, DashboardSummary, MonthlySummary
from app.schemas.transaction import TransactionRead
from app.services.account_service import list_accounts, total_balance
from app.services.exceptions import ValidationError
from app.services.transaction_service import list_recent_transactions
from app.utils.date_helpers import now_in_timezone


def _coerce_decimal(value: object) -> Decimal:
    if value is None:
        return Decimal("0.00")
    if isinstance(value, Decimal):
        return value.quantize(Decimal("0.01"))
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _percentage(part: Decimal, total: Decimal) -> Decimal:
    if total == 0:
        return Decimal("0.00")
    return ((part / total) * Decimal("100")).quantize(Decimal("0.01"))


def _month_range(month: int | None, year: int | None) -> tuple[int, int, date, date]:
    today = now_in_timezone().date()
    month = month or today.month
    year = year or today.year
    if month < 1 or month > 12:
        raise ValidationError("Mes deve estar entre 1 e 12.")
    if year < 2000:
        raise ValidationError("Ano deve ser maior ou igual a 2000.")
    last_day = monthrange(year, month)[1]
    return month, year, date(year, month, 1), date(year, month, last_day)


def _sum_transactions(
    session: Session,
    user_id: int,
    type_: str,
    start_date: date,
    end_date: date,
) -> Decimal:
    value = session.exec(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == type_,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        ),
    ).one()
    return _coerce_decimal(value)


def _expenses_by_category(
    session: Session,
    user_id: int,
    start_date: date,
    end_date: date,
    total_expense: Decimal,
) -> list[CategorySpending]:
    rows = session.exec(
        select(
            Transaction.category_id,
            Category.name,
            func.sum(Transaction.amount),
        )
        .select_from(Transaction)
        .join(Category, Transaction.category_id == Category.id, isouter=True)
        .where(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        )
        .group_by(Transaction.category_id, Category.name)
        .order_by(func.sum(Transaction.amount).desc()),
    ).all()

    result: list[CategorySpending] = []
    for category_id, category_name, total in rows:
        category_total = _coerce_decimal(total)
        result.append(
            CategorySpending(
                category_id=category_id,
                category_name=category_name or "Sem categoria",
                total=category_total,
                percentage=_percentage(category_total, total_expense),
            ),
        )
    return result


def get_monthly_summary(
    session: Session,
    user_id: int,
    month: int | None = None,
    year: int | None = None,
) -> MonthlySummary:
    month, year, start_date, end_date = _month_range(month, year)
    total_income = _sum_transactions(session, user_id, "income", start_date, end_date)
    total_expense = _sum_transactions(session, user_id, "expense", start_date, end_date)
    categories = _expenses_by_category(session, user_id, start_date, end_date, total_expense)

    return MonthlySummary(
        month=month,
        year=year,
        total_income=total_income,
        total_expense=total_expense,
        balance=(total_income - total_expense).quantize(Decimal("0.01")),
        expenses_by_category=categories,
        top_expenses=categories[:3],
    )


def get_balance_summary(session: Session, user_id: int) -> AccountBalanceSummary:
    accounts = list_accounts(session, user_id)
    return AccountBalanceSummary(
        total=total_balance(accounts),
        accounts=[AccountBalanceItem.model_validate(account) for account in accounts],
    )


def _total_reserved(session: Session, user_id: int) -> Decimal:
    value = session.exec(
        select(func.coalesce(func.sum(Reserve.current_value), 0)).where(
            Reserve.user_id == user_id,
            Reserve.is_active == True,
        ),
    ).one()
    return _coerce_decimal(value)


def get_dashboard_summary(
    session: Session,
    user_id: int,
    month: int | None = None,
    year: int | None = None,
) -> DashboardSummary:
    monthly = get_monthly_summary(session, user_id, month, year)
    accounts = list_accounts(session, user_id)
    recent_transactions = list_recent_transactions(session, user_id, limit=5)

    return DashboardSummary(
        month=monthly.month,
        year=monthly.year,
        total_income=monthly.total_income,
        total_expense=monthly.total_expense,
        monthly_balance=monthly.balance,
        total_reserved=_total_reserved(session, user_id),
        total_account_balance=total_balance(accounts),
        accounts=[AccountBalanceItem.model_validate(account) for account in accounts],
        recent_transactions=[
            TransactionRead.model_validate(transaction)
            for transaction in recent_transactions
        ],
    )
