from datetime import date
from decimal import Decimal

from app.schemas.effect import ExpenseEffectSimulation
from app.telegram.parser import ParseError
from app.telegram.responses import (
    format_expense_effect,
    format_parse_error,
    format_reserves,
    format_service_error,
)


def test_parse_error_includes_help_hint() -> None:
    message = format_parse_error(
        ParseError(
            error_type="no_amount",
            message="Nao consegui identificar o valor.",
            suggestion="Tente: mercado 45",
        ),
    )

    assert "Sugestao: Tente: mercado 45" in message
    assert "/ajuda" in message


def test_service_error_is_clear_to_user() -> None:
    message = format_service_error("Saldo insuficiente para aportar na reserva.")

    assert "Nao consegui concluir essa acao." in message
    assert "Saldo insuficiente" in message


def test_empty_reserves_has_clear_message() -> None:
    assert format_reserves([]) == "Voce ainda nao tem reservas ativas cadastradas."


def test_format_expense_effect_makes_clear_it_is_simulation() -> None:
    message = format_expense_effect(
        ExpenseEffectSimulation(
            description="Pizza",
            amount=Decimal("42.00"),
            date=date(2026, 5, 3),
            category_name="Alimentacao",
            current_account_balance=Decimal("1000.00"),
            projected_account_balance=Decimal("958.00"),
            current_monthly_balance=Decimal("1200.00"),
            projected_monthly_balance=Decimal("1158.00"),
            current_plan_remaining=Decimal("820.00"),
            projected_plan_remaining=Decimal("778.00"),
        ),
    )

    assert "Simulacao de despesa" in message
    assert "Nada foi registrado" in message
    assert "Pizza" in message
