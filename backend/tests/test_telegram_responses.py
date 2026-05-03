from datetime import date, datetime
from decimal import Decimal

from app.schemas.effect import ExpenseEffectSimulation
from app.schemas.reset import PendingReset, ResetResult
from app.telegram.parser import ParseError
from app.telegram.responses import (
    format_expense_effect,
    format_parse_error,
    format_reset_refused,
    format_reset_request,
    format_reset_success,
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


def test_format_reset_request_includes_confirmation_code() -> None:
    message = format_reset_request(
        PendingReset(
            chat_id=123,
            user_id=1,
            confirmation_code="123456",
            initial_balance=Decimal("5000.00"),
            expires_at=datetime(2026, 5, 3, 12, 0, 0),
        ),
    )

    assert "Reset administrativo solicitado" in message
    assert "/confirmar_reset 123456" in message
    assert "R$ 5.000,00" in message


def test_format_reset_success_and_refusal_are_clear() -> None:
    success = format_reset_success(
        ResetResult(
            user_id=1,
            initial_balance=Decimal("5000.00"),
            deleted_transactions=1,
            deleted_accounts=2,
            deleted_categories=14,
            deleted_reserves=3,
            deleted_budgets=0,
            deleted_monthly_plans=0,
            deleted_allocation_rules=4,
        ),
    )
    refused = format_reset_refused("confirmacao invalida.")

    assert "Reset concluido" in success
    assert "R$ 5.000,00" in success
    assert "Nao executei o reset" in refused
    assert "confirmacao invalida" in refused
