from datetime import date
from decimal import Decimal

from sqlmodel import Session

from app.schemas.transaction import TransactionCreate
from app.services.chart_service import generate_bars_chart, generate_pie_chart
from app.services.transaction_service import create_expense, create_income

USER_ID = 1


def test_chart_pie_returns_png_bytes(session: Session, basic_data: dict[str, object]) -> None:
    food = basic_data["food"]
    create_expense(
        session,
        USER_ID,
        TransactionCreate(
            type="expense",
            amount=Decimal("50.00"),
            description="Mercado",
            category_id=food.id,
            date=date(2026, 5, 2),
        ),
    )

    image = generate_pie_chart(session, USER_ID, month=5, year=2026)
    assert image.read(8) == b"\x89PNG\r\n\x1a\n"


def test_chart_bars_returns_png_bytes(session: Session, basic_data: dict[str, object]) -> None:
    salary = basic_data["salary"]
    create_income(
        session,
        USER_ID,
        TransactionCreate(
            type="income",
            amount=Decimal("1000.00"),
            description="Salario",
            category_id=salary.id,
            date=date(2026, 5, 2),
        ),
    )

    image = generate_bars_chart(session, USER_ID, months=6)
    assert image.read(8) == b"\x89PNG\r\n\x1a\n"
