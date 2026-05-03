from datetime import date
from decimal import Decimal

from sqlmodel import Session

from app.schemas.effect import (
    AllocationEffect,
    BudgetEffect,
    ExpenseEffectSimulation,
)
from app.services.account_service import get_default_account
from app.services.budget_service import get_budget_progress
from app.services.category_service import get_category_or_none
from app.services.plan_service import get_plan_progress
from app.services.summary_service import get_monthly_summary
from app.utils.date_helpers import now_in_timezone


def _money(value: Decimal | int | str) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _percentage(part: Decimal, total: Decimal) -> Decimal:
    if total <= 0:
        return Decimal("0.00")
    return ((part / total) * Decimal("100")).quantize(Decimal("0.01"))


def _budget_alert(projected_percentage: Decimal, category_name: str) -> str | None:
    if projected_percentage >= 100:
        return f"Voce ultrapassaria o limite de {category_name} este mes."
    if projected_percentage >= 80:
        return f"Isso deixa {category_name} acima de 80% do orcamento."
    return None


def simulate_expense_effect(
    session: Session,
    user_id: int,
    amount: Decimal,
    description: str,
    category_id: int | None = None,
    effect_date: date | None = None,
) -> ExpenseEffectSimulation:
    amount = _money(amount)
    effect_date = effect_date or now_in_timezone().date()
    account = get_default_account(session, user_id)
    category = get_category_or_none(session, user_id, category_id)

    summary = get_monthly_summary(
        session,
        user_id,
        month=effect_date.month,
        year=effect_date.year,
    )
    plan_progress = get_plan_progress(
        session,
        user_id,
        month=effect_date.month,
        year=effect_date.year,
    )

    current_account_balance = _money(account.current_balance)
    projected_account_balance = _money(current_account_balance - amount)
    current_monthly_balance = _money(summary.balance)
    projected_monthly_balance = _money(current_monthly_balance - amount)
    current_plan_remaining = _money(plan_progress.plan.free_amount - summary.total_expense)
    projected_plan_remaining = _money(current_plan_remaining - amount)

    alerts: list[str] = []
    if projected_account_balance < 0:
        alerts.append("Essa despesa deixaria o saldo da conta negativo.")
    if projected_plan_remaining < 0:
        alerts.append("Essa despesa passaria do valor livre planejado para o mes.")

    budget_effect = None
    if category and category.type == "expense":
        budget = get_budget_progress(
            session,
            user_id,
            category.id,
            month=effect_date.month,
            year=effect_date.year,
        )
        if budget:
            projected_spent = _money(budget.spent_value + amount)
            projected_percentage = _percentage(projected_spent, budget.limit_value)
            alert_message = _budget_alert(projected_percentage, budget.category_name)
            if alert_message:
                alerts.append(alert_message)
            budget_effect = BudgetEffect(
                category_id=budget.category_id,
                category_name=budget.category_name,
                limit_value=budget.limit_value,
                current_spent=budget.spent_value,
                projected_spent=projected_spent,
                current_percentage=budget.percentage_used,
                projected_percentage=projected_percentage,
                alert_message=alert_message,
            )

    allocation_effect = None
    if category:
        allocation = next(
            (
                item
                for item in plan_progress.allocations
                if item.category_id == category.id
            ),
            None,
        )
        if allocation:
            projected_spent = _money(allocation.spent_amount + amount)
            projected_percentage = _percentage(projected_spent, allocation.planned_amount)
            alert_message = None
            if allocation.planned_amount > 0 and projected_spent > allocation.planned_amount:
                alert_message = f"Essa despesa ultrapassaria a fatia de {allocation.name}."
                alerts.append(alert_message)
            allocation_effect = AllocationEffect(
                rule_id=allocation.rule_id,
                name=allocation.name,
                planned_amount=allocation.planned_amount,
                current_spent=allocation.spent_amount,
                projected_spent=projected_spent,
                current_percentage=allocation.used_percentage,
                projected_percentage=projected_percentage,
                emoji=allocation.emoji,
                alert_message=alert_message,
            )

    return ExpenseEffectSimulation(
        description=description,
        amount=amount,
        date=effect_date,
        category_id=category.id if category else None,
        category_name=category.name if category else "Outros",
        current_account_balance=current_account_balance,
        projected_account_balance=projected_account_balance,
        current_monthly_balance=current_monthly_balance,
        projected_monthly_balance=projected_monthly_balance,
        current_plan_remaining=current_plan_remaining,
        projected_plan_remaining=projected_plan_remaining,
        budget=budget_effect,
        allocation=allocation_effect,
        alerts=list(dict.fromkeys(alerts)),
    )
