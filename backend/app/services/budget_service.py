from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Budget, Category, Transaction
from app.schemas.budget import BudgetProgress, BudgetRead
from app.services.atomic import atomic_write
from app.services.category_service import get_category
from app.services.exceptions import NotFoundError, ValidationError
from app.utils.date_helpers import now_in_timezone


def _money(value: Decimal | int | str) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _month_range(month: int | None = None, year: int | None = None) -> tuple[int, int, date, date]:
    today = now_in_timezone().date()
    month = month or today.month
    year = year or today.year
    if month < 1 or month > 12:
        raise ValidationError("Mes deve estar entre 1 e 12.")
    if year < 2000:
        raise ValidationError("Ano deve ser maior ou igual a 2000.")
    return month, year, date(year, month, 1), date(year, month, monthrange(year, month)[1])


def get_budget(
    session: Session,
    user_id: int,
    category_id: int,
    month: int,
    year: int,
) -> Budget | None:
    return session.exec(
        select(Budget).where(
            Budget.user_id == user_id,
            Budget.category_id == category_id,
            Budget.month == month,
            Budget.year == year,
        ),
    ).first()


def list_budgets(
    session: Session,
    user_id: int,
    month: int | None = None,
    year: int | None = None,
) -> list[BudgetRead]:
    statement = select(Budget).where(Budget.user_id == user_id)
    if month is not None:
        statement = statement.where(Budget.month == month)
    if year is not None:
        statement = statement.where(Budget.year == year)
    budgets = session.exec(statement.order_by(Budget.year.desc(), Budget.month.desc())).all()
    return [BudgetRead.model_validate(budget) for budget in budgets]


def upsert_budget(
    session: Session,
    user_id: int,
    category_id: int,
    month: int,
    year: int,
    limit_value: Decimal,
) -> Budget:
    category = get_category(session, user_id, category_id)
    if category.type != "expense":
        raise ValidationError("Orcamento so pode ser criado para categoria de despesa.")

    month, year, _, _ = _month_range(month, year)
    limit_value = _money(limit_value)
    if limit_value < 0:
        raise ValidationError("Limite do orcamento nao pode ser negativo.")

    budget = get_budget(session, user_id, category_id, month, year)
    if budget:
        budget.limit_value = limit_value
    else:
        budget = Budget(
            user_id=user_id,
            category_id=category_id,
            month=month,
            year=year,
            limit_value=limit_value,
        )

    with atomic_write(session):
        session.add(budget)
    session.refresh(budget)
    return budget


def _spent_for_category(
    session: Session,
    user_id: int,
    category_id: int,
    start_date: date,
    end_date: date,
) -> Decimal:
    spent = session.exec(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.category_id == category_id,
            Transaction.type == "expense",
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        ),
    ).one()
    return _money(spent)


def _alert_for(percentage_used: Decimal, category_name: str) -> tuple[str | None, str | None]:
    if percentage_used >= 100:
        return (
            "exceeded",
            f"Voce ultrapassou o limite de {category_name} este mes.",
        )
    if percentage_used >= 80:
        return (
            "warning",
            f"Atencao: voce ja usou {percentage_used}% do orcamento de {category_name} este mes.",
        )
    return None, None


def get_budget_progress(
    session: Session,
    user_id: int,
    category_id: int,
    month: int | None = None,
    year: int | None = None,
) -> BudgetProgress | None:
    month, year, start_date, end_date = _month_range(month, year)
    category = get_category(session, user_id, category_id)
    if category.type != "expense":
        return None

    budget = get_budget(session, user_id, category_id, month, year)
    limit_value = budget.limit_value if budget else category.monthly_limit
    if limit_value is None:
        return None

    limit_value = _money(limit_value)
    spent_value = _spent_for_category(session, user_id, category_id, start_date, end_date)
    percentage_used = Decimal("0.00")
    if limit_value > 0:
        percentage_used = ((spent_value / limit_value) * Decimal("100")).quantize(Decimal("0.01"))

    alert_level, alert_message = _alert_for(percentage_used, category.name)
    return BudgetProgress(
        category_id=category.id,
        category_name=category.name,
        month=month,
        year=year,
        limit_value=limit_value,
        spent_value=spent_value,
        percentage_used=percentage_used,
        alert_level=alert_level,
        alert_message=alert_message,
    )


def list_budget_progress(
    session: Session,
    user_id: int,
    month: int | None = None,
    year: int | None = None,
) -> list[BudgetProgress]:
    month, year, _, _ = _month_range(month, year)
    categories = session.exec(
        select(Category).where(
            Category.user_id == user_id,
            Category.type == "expense",
            Category.is_active == True,
        ),
    ).all()

    progress: list[BudgetProgress] = []
    for category in categories:
        item = get_budget_progress(session, user_id, category.id, month, year)
        if item:
            progress.append(item)
    return progress


def ensure_budget_exists(
    session: Session,
    user_id: int,
    category_id: int,
    month: int,
    year: int,
) -> Budget:
    budget = get_budget(session, user_id, category_id, month, year)
    if not budget:
        raise NotFoundError("Orcamento nao encontrado.")
    return budget
