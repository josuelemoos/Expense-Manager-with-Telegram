from datetime import date
from decimal import Decimal

from sqlmodel import Session

from app.schemas.transaction import TransactionCreate
from app.services.budget_service import get_budget_progress, upsert_budget
from app.services.summary_service import get_balance_summary, get_monthly_summary
from app.services.transaction_service import create_expense, create_income

USER_ID = 1


def test_monthly_summary_correct_totals(session: Session, basic_data: dict[str, object]) -> None:
    food = basic_data["food"]
    salary = basic_data["salary"]

    create_income(
        session,
        USER_ID,
        TransactionCreate(
            type="income",
            amount=Decimal("3000.00"),
            description="Salario",
            category_id=salary.id,
            date=date(2026, 5, 2),
        ),
    )
    create_expense(
        session,
        USER_ID,
        TransactionCreate(
            type="expense",
            amount=Decimal("500.00"),
            description="Mercado",
            category_id=food.id,
            date=date(2026, 5, 3),
        ),
    )

    summary = get_monthly_summary(session, USER_ID, month=5, year=2026)
    assert summary.total_income == Decimal("3000.00")
    assert summary.total_expense == Decimal("500.00")
    assert summary.balance == Decimal("2500.00")
    assert summary.top_expenses[0].category_name == "Alimentacao"


def test_budget_alert_at_80_percent(session: Session, basic_data: dict[str, object]) -> None:
    food = basic_data["food"]
    upsert_budget(session, USER_ID, food.id, month=5, year=2026, limit_value=Decimal("500.00"))

    create_expense(
        session,
        USER_ID,
        TransactionCreate(
            type="expense",
            amount=Decimal("400.00"),
            description="Mercado",
            category_id=food.id,
            date=date(2026, 5, 4),
        ),
    )

    progress = get_budget_progress(session, USER_ID, food.id, month=5, year=2026)
    assert progress is not None
    assert progress.percentage_used == Decimal("80.00")
    assert progress.alert_level == "warning"


def test_balance_summary_totals_accounts(session: Session, basic_data: dict[str, object]) -> None:
    summary = get_balance_summary(session, USER_ID)
    assert summary.total == Decimal("1000.00")
    assert len(summary.accounts) == 1
