from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import AllocationRule, MonthlyPlan, Transaction
from app.schemas.plan import (
    AllocationProgress,
    AllocationRuleRead,
    AllocationRuleUpsert,
    MonthlyPlanRead,
    MonthlyPlanUpsert,
    PlanProgress,
)
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


def _validate_plan_values(expected_income: Decimal, committed_expenses: Decimal) -> None:
    if expected_income < 0 or committed_expenses < 0:
        raise ValidationError("Valores do plano nao podem ser negativos.")
    if committed_expenses > expected_income:
        raise ValidationError("Comprometido nao pode ser maior que a renda esperada.")


def get_monthly_plan(
    session: Session,
    user_id: int,
    month: int | None = None,
    year: int | None = None,
) -> MonthlyPlan | None:
    month, year, _, _ = _month_range(month, year)
    return session.exec(
        select(MonthlyPlan).where(
            MonthlyPlan.user_id == user_id,
            MonthlyPlan.month == month,
            MonthlyPlan.year == year,
        ),
    ).first()


def get_monthly_plan_read(
    session: Session,
    user_id: int,
    month: int | None = None,
    year: int | None = None,
) -> MonthlyPlanRead:
    month, year, _, _ = _month_range(month, year)
    plan = get_monthly_plan(session, user_id, month, year)
    if plan:
        return MonthlyPlanRead.model_validate(plan)
    return MonthlyPlanRead(
        user_id=user_id,
        month=month,
        year=year,
        expected_income=Decimal("0.00"),
        committed_expenses=Decimal("0.00"),
        warning="Nao existe plano para este mes.",
    )


def upsert_monthly_plan(
    session: Session,
    user_id: int,
    data: MonthlyPlanUpsert,
) -> MonthlyPlanRead:
    expected_income = _money(data.expected_income)
    committed_expenses = _money(data.committed_expenses)
    _validate_plan_values(expected_income, committed_expenses)

    plan = get_monthly_plan(session, user_id, data.month, data.year)
    now = now_in_timezone().replace(tzinfo=None)
    if plan:
        plan.expected_income = expected_income
        plan.committed_expenses = committed_expenses
        plan.notes = data.notes
        plan.updated_at = now
    else:
        plan = MonthlyPlan(
            user_id=user_id,
            month=data.month,
            year=data.year,
            expected_income=expected_income,
            committed_expenses=committed_expenses,
            notes=data.notes,
            updated_at=now,
        )

    session.add(plan)
    session.commit()
    session.refresh(plan)
    return MonthlyPlanRead.model_validate(plan)


def list_allocation_rules(session: Session, user_id: int) -> list[AllocationRuleRead]:
    rules = session.exec(
        select(AllocationRule)
        .where(AllocationRule.user_id == user_id, AllocationRule.is_active == True)
        .order_by(AllocationRule.sort_order, AllocationRule.name),
    ).all()
    return [AllocationRuleRead.model_validate(rule) for rule in rules]


def _total_active_percentage(
    session: Session,
    user_id: int,
    replacing_rule_id: int | None = None,
    replacement_percentage: Decimal | None = None,
    replacement_active: bool = True,
) -> Decimal:
    rules = session.exec(
        select(AllocationRule).where(AllocationRule.user_id == user_id),
    ).all()

    total = Decimal("0.00")
    found_replacement = False
    for rule in rules:
        if replacing_rule_id and rule.id == replacing_rule_id:
            found_replacement = True
            if replacement_active:
                total += replacement_percentage or Decimal("0.00")
            continue
        if rule.is_active:
            total += rule.percentage

    if replacing_rule_id is None and replacement_active:
        total += replacement_percentage or Decimal("0.00")
    elif replacing_rule_id and not found_replacement:
        raise NotFoundError("Regra de alocacao nao encontrada.")

    return total.quantize(Decimal("0.01"))


def validate_allocation_percentages(
    session: Session,
    user_id: int,
    replacing_rule_id: int | None = None,
    replacement_percentage: Decimal | None = None,
    replacement_active: bool = True,
) -> Decimal:
    total = _total_active_percentage(
        session=session,
        user_id=user_id,
        replacing_rule_id=replacing_rule_id,
        replacement_percentage=replacement_percentage,
        replacement_active=replacement_active,
    )
    if total > Decimal("100.00"):
        raise ValidationError("A soma das alocacoes ativas nao pode ultrapassar 100%.")
    return total


def upsert_allocation_rule(
    session: Session,
    user_id: int,
    data: AllocationRuleUpsert,
) -> AllocationRuleRead:
    if data.category_id is not None:
        get_category(session, user_id, data.category_id)

    percentage = data.percentage.quantize(Decimal("0.01"))
    validate_allocation_percentages(
        session=session,
        user_id=user_id,
        replacing_rule_id=data.id,
        replacement_percentage=percentage,
        replacement_active=data.is_active,
    )

    if data.id:
        rule = session.exec(
            select(AllocationRule).where(
                AllocationRule.id == data.id,
                AllocationRule.user_id == user_id,
            ),
        ).first()
        if not rule:
            raise NotFoundError("Regra de alocacao nao encontrada.")
        rule.name = data.name.strip()
        rule.percentage = percentage
        rule.category_id = data.category_id
        rule.emoji = data.emoji
        rule.sort_order = data.sort_order
        rule.is_active = data.is_active
    else:
        rule = AllocationRule(
            user_id=user_id,
            name=data.name.strip(),
            percentage=percentage,
            category_id=data.category_id,
            emoji=data.emoji,
            sort_order=data.sort_order,
            is_active=data.is_active,
        )

    session.add(rule)
    session.commit()
    session.refresh(rule)
    return AllocationRuleRead.model_validate(rule)


def _spent_for_category(
    session: Session,
    user_id: int,
    category_id: int | None,
    start_date: date,
    end_date: date,
) -> Decimal:
    if category_id is None:
        return Decimal("0.00")

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


def get_plan_progress(
    session: Session,
    user_id: int,
    month: int | None = None,
    year: int | None = None,
) -> PlanProgress:
    month, year, start_date, end_date = _month_range(month, year)
    plan = get_monthly_plan_read(session, user_id, month, year)
    free_amount = plan.free_amount
    rules = session.exec(
        select(AllocationRule)
        .where(AllocationRule.user_id == user_id, AllocationRule.is_active == True)
        .order_by(AllocationRule.sort_order, AllocationRule.name),
    ).all()

    allocations: list[AllocationProgress] = []
    allocated_percentage = Decimal("0.00")
    for rule in rules:
        planned_amount = (free_amount * (rule.percentage / Decimal("100"))).quantize(Decimal("0.01"))
        spent_amount = _spent_for_category(
            session,
            user_id,
            rule.category_id,
            start_date,
            end_date,
        )
        used_percentage = Decimal("0.00")
        if planned_amount > 0:
            used_percentage = ((spent_amount / planned_amount) * Decimal("100")).quantize(Decimal("0.01"))
        is_over = spent_amount > planned_amount and planned_amount > 0
        allocations.append(
            AllocationProgress(
                rule_id=rule.id,
                name=rule.name,
                percentage=rule.percentage,
                planned_amount=planned_amount,
                spent_amount=spent_amount,
                used_percentage=used_percentage,
                category_id=rule.category_id,
                emoji=rule.emoji,
                is_over=is_over,
                alert_message=(
                    f"Fatia de {rule.name} ultrapassada."
                    if is_over
                    else None
                ),
            ),
        )
        allocated_percentage += rule.percentage

    unallocated_percentage = (Decimal("100.00") - allocated_percentage).quantize(Decimal("0.01"))
    if unallocated_percentage < 0:
        unallocated_percentage = Decimal("0.00")

    return PlanProgress(
        plan=plan,
        allocations=allocations,
        unallocated_percentage=unallocated_percentage,
        unallocated_amount=(free_amount * (unallocated_percentage / Decimal("100"))).quantize(Decimal("0.01")),
    )
