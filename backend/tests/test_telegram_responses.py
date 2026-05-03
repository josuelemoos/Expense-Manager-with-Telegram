from app.telegram.parser import ParseError
from app.telegram.responses import format_parse_error, format_reserves, format_service_error


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
