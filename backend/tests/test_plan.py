from datetime import date
from decimal import Decimal

import pytest
from sqlmodel import Session
from sqlmodel import select

from app.models import Transaction
from app.schemas.plan import AllocationRuleUpsert, MonthlyPlanUpsert
from app.schemas.transaction import TransactionCreate
from app.services.exceptions import ValidationError
from app.services.effect_service import simulate_expense_effect
from app.services.plan_service import (
    get_plan_progress,
    upsert_allocation_rule,
    upsert_monthly_plan,
    validate_allocation_percentages,
)
from app.services.transaction_service import create_expense

USER_ID = 1


def test_plan_free_amount_calculated_correctly(
    session: Session,
    basic_data: dict[str, object],
) -> None:
    plan = upsert_monthly_plan(
        session,
        USER_ID,
        MonthlyPlanUpsert(
            month=5,
            year=2026,
            expected_income=Decimal("3000.00"),
            committed_expenses=Decimal("1800.00"),
        ),
    )

    assert plan.free_amount == Decimal("1200.00")


def test_plan_fails_if_committed_exceeds_income(
    session: Session,
    basic_data: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        upsert_monthly_plan(
            session,
            USER_ID,
            MonthlyPlanUpsert(
                month=5,
                year=2026,
                expected_income=Decimal("1000.00"),
                committed_expenses=Decimal("1200.00"),
            ),
        )


def test_allocation_percentages_sum_to_100(
    session: Session,
    basic_data: dict[str, object],
) -> None:
    total = validate_allocation_percentages(session, USER_ID)
    assert total == Decimal("40.00")

    upsert_allocation_rule(
        session,
        USER_ID,
        AllocationRuleUpsert(
            name="Investimentos",
            percentage=Decimal("60.00"),
            sort_order=3,
        ),
    )
    assert validate_allocation_percentages(session, USER_ID) == Decimal("100.00")

    with pytest.raises(ValidationError):
        upsert_allocation_rule(
            session,
            USER_ID,
            AllocationRuleUpsert(
                name="Extra",
                percentage=Decimal("1.00"),
                sort_order=4,
            ),
        )


def test_plan_progress_compares_real_spending(
    session: Session,
    basic_data: dict[str, object],
) -> None:
    leisure = basic_data["leisure"]
    upsert_monthly_plan(
        session,
        USER_ID,
        MonthlyPlanUpsert(
            month=5,
            year=2026,
            expected_income=Decimal("3000.00"),
            committed_expenses=Decimal("1800.00"),
        ),
    )
    create_expense(
        session,
        USER_ID,
        TransactionCreate(
            type="expense",
            amount=Decimal("120.00"),
            description="Cinema",
            category_id=leisure.id,
            date=date(2026, 5, 10),
        ),
    )

    progress = get_plan_progress(session, USER_ID, month=5, year=2026)
    leisure_progress = next(item for item in progress.allocations if item.name == "Lazer")
    assert leisure_progress.planned_amount == Decimal("240.00")
    assert leisure_progress.spent_amount == Decimal("120.00")
    assert leisure_progress.used_percentage == Decimal("50.00")


def test_simulate_expense_effect_does_not_persist(
    session: Session,
    basic_data: dict[str, object],
) -> None:
    account = basic_data["account"]
    food = basic_data["food"]
    upsert_monthly_plan(
        session,
        USER_ID,
        MonthlyPlanUpsert(
            month=5,
            year=2026,
            expected_income=Decimal("3000.00"),
            committed_expenses=Decimal("1800.00"),
        ),
    )

    result = simulate_expense_effect(
        session,
        USER_ID,
        amount=Decimal("42.00"),
        description="Pizza",
        category_id=food.id,
        effect_date=date(2026, 5, 3),
    )

    session.refresh(account)
    transactions = session.exec(select(Transaction)).all()
    assert account.current_balance == Decimal("1000.00")
    assert transactions == []
    assert result.projected_account_balance == Decimal("958.00")


def test_simulate_expense_effect_updates_projection(
    session: Session,
    basic_data: dict[str, object],
) -> None:
    food = basic_data["food"]
    upsert_monthly_plan(
        session,
        USER_ID,
        MonthlyPlanUpsert(
            month=5,
            year=2026,
            expected_income=Decimal("3000.00"),
            committed_expenses=Decimal("1800.00"),
        ),
    )
    create_expense(
        session,
        USER_ID,
        TransactionCreate(
            type="expense",
            amount=Decimal("380.00"),
            description="Mercado",
            category_id=food.id,
            date=date(2026, 5, 2),
        ),
    )

    result = simulate_expense_effect(
        session,
        USER_ID,
        amount=Decimal("42.00"),
        description="Pizza",
        category_id=food.id,
        effect_date=date(2026, 5, 3),
    )

    assert result.current_account_balance == Decimal("620.00")
    assert result.projected_account_balance == Decimal("578.00")
    assert result.current_monthly_balance == Decimal("-380.00")
    assert result.projected_monthly_balance == Decimal("-422.00")
    assert result.current_plan_remaining == Decimal("820.00")
    assert result.projected_plan_remaining == Decimal("778.00")
    assert result.budget is not None
    assert result.budget.current_spent == Decimal("380.00")
    assert result.budget.projected_spent == Decimal("422.00")
    assert result.budget.projected_percentage == Decimal("84.40")
    assert result.budget.alert_message is not None
