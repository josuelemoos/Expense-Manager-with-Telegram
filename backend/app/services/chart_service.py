from calendar import monthrange
from datetime import date
from decimal import Decimal
from io import BytesIO

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Category, Transaction
from app.services.exceptions import ValidationError
from app.utils.date_helpers import now_in_timezone


CHART_COLORS = [
    "#6366f1",
    "#f59e0b",
    "#10b981",
    "#ef4444",
    "#8b5cf6",
    "#3b82f6",
    "#f97316",
]


def _month_range(month: int | None = None, year: int | None = None) -> tuple[int, int, date, date]:
    today = now_in_timezone().date()
    month = month or today.month
    year = year or today.year
    if month < 1 or month > 12:
        raise ValidationError("Mes deve estar entre 1 e 12.")
    if year < 2000:
        raise ValidationError("Ano deve ser maior ou igual a 2000.")
    return month, year, date(year, month, 1), date(year, month, monthrange(year, month)[1])


def _png_from_current_figure() -> BytesIO:
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png", dpi=150, facecolor="#ffffff")
    plt.close()
    buffer.seek(0)
    return buffer


def generate_pie_chart(
    session: Session,
    user_id: int,
    month: int | None = None,
    year: int | None = None,
) -> BytesIO:
    month, year, start_date, end_date = _month_range(month, year)
    rows = session.exec(
        select(Category.name, func.sum(Transaction.amount))
        .select_from(Transaction)
        .join(Category, Transaction.category_id == Category.id, isouter=True)
        .where(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        )
        .group_by(Category.name)
        .order_by(func.sum(Transaction.amount).desc()),
    ).all()

    labels: list[str] = []
    values: list[Decimal] = []
    for category_name, total in rows:
        total_value = Decimal(str(total or 0)).quantize(Decimal("0.01"))
        if total_value > 0:
            labels.append(category_name or "Sem categoria")
            values.append(total_value)

    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, ax = plt.subplots(figsize=(6, 4), facecolor="#ffffff")
    ax.set_title(f"Gastos por categoria - {month:02d}/{year}", fontsize=13, fontweight="bold")

    if not values:
        ax.text(0.5, 0.5, "Sem despesas no periodo", ha="center", va="center")
        ax.axis("off")
        return _png_from_current_figure()

    ax.pie(
        [float(value) for value in values],
        labels=labels,
        autopct="%1.1f%%",
        colors=CHART_COLORS[: len(values)],
        startangle=90,
    )
    ax.axis("equal")
    return _png_from_current_figure()


def _last_months(count: int) -> list[tuple[int, int]]:
    today = now_in_timezone().date()
    month = today.month
    year = today.year
    months: list[tuple[int, int]] = []
    for _ in range(count):
        months.append((month, year))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return list(reversed(months))


def _sum_for_period(
    session: Session,
    user_id: int,
    type_: str,
    start_date: date,
    end_date: date,
) -> Decimal:
    total = session.exec(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == type_,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        ),
    ).one()
    return Decimal(str(total or 0)).quantize(Decimal("0.01"))


def generate_bars_chart(
    session: Session,
    user_id: int,
    months: int = 6,
) -> BytesIO:
    if months < 1 or months > 24:
        raise ValidationError("Quantidade de meses deve estar entre 1 e 24.")

    labels: list[str] = []
    incomes: list[float] = []
    expenses: list[float] = []
    for month, year in _last_months(months):
        _, _, start_date, end_date = _month_range(month, year)
        labels.append(f"{month:02d}/{str(year)[-2:]}")
        incomes.append(float(_sum_for_period(session, user_id, "income", start_date, end_date)))
        expenses.append(float(_sum_for_period(session, user_id, "expense", start_date, end_date)))

    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, ax = plt.subplots(figsize=(7, 4), facecolor="#ffffff")
    indexes = range(len(labels))
    width = 0.36
    ax.bar([index - width / 2 for index in indexes], incomes, width, label="Receitas", color="#10b981")
    ax.bar([index + width / 2 for index in indexes], expenses, width, label="Despesas", color="#ef4444")
    ax.set_title(f"Receitas vs despesas - ultimos {months} meses", fontsize=13, fontweight="bold")
    ax.set_xticks(list(indexes))
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(axis="y", alpha=0.2)
    return _png_from_current_figure()
