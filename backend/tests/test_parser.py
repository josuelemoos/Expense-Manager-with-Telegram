from app.telegram.parser import ParseError, ParsedMessage, parse_message


def assert_parsed(text: str) -> ParsedMessage:
    parsed = parse_message(text)
    assert isinstance(parsed, ParsedMessage)
    return parsed


def assert_error(text: str) -> ParseError:
    parsed = parse_message(text)
    assert isinstance(parsed, ParseError)
    return parsed


def test_parse_expense_simple() -> None:
    parsed = assert_parsed("mercado 45")
    assert parsed.intent == "expense"
    assert parsed.amount == 45
    assert parsed.suggested_category == "Alimenta\u00e7\u00e3o"


def test_parse_expense_with_prefix() -> None:
    parsed = assert_parsed("gastei 30 uber")
    assert parsed.intent == "expense"
    assert parsed.amount == 30
    assert parsed.suggested_category == "Transporte"


def test_parse_income_recebi() -> None:
    parsed = assert_parsed("recebi 1500")
    assert parsed.intent == "income"
    assert parsed.amount == 1500
    assert parsed.suggested_category == "Outros"


def test_parse_income_salario() -> None:
    parsed = assert_parsed("sal\u00e1rio 2000")
    assert parsed.intent == "income"
    assert parsed.amount == 2000
    assert parsed.suggested_category == "Sal\u00e1rio"


def test_parse_reserve_deposit() -> None:
    parsed = assert_parsed("guardei 100 reserva")
    assert parsed.intent == "reserve_deposit"
    assert parsed.amount == 100


def test_parse_no_amount_returns_error() -> None:
    error = assert_error("mercado")
    assert error.error_type == "no_amount"


def test_parse_only_number_ambiguous() -> None:
    error = assert_error("45")
    assert error.error_type == "ambiguous"


def test_parse_query_balance() -> None:
    parsed = assert_parsed("quanto tenho?")
    assert parsed.intent == "query_balance"


def test_parse_chart_pie() -> None:
    parsed = assert_parsed("/grafico")
    assert parsed.intent == "chart_pie"


def test_parse_chart_bars() -> None:
    parsed = assert_parsed("/grafico barras")
    assert parsed.intent == "chart_bars"


def test_parse_expense_effect() -> None:
    parsed = assert_parsed("/efeito pizza de 42 reais hoje")
    assert parsed.intent == "simulate_expense_effect"
    assert parsed.amount == 42
    assert parsed.description == "Pizza"
    assert parsed.suggested_category == "Alimenta\u00e7\u00e3o"
    assert parsed.date is not None


def test_parse_set_income() -> None:
    parsed = assert_parsed("definir renda 3000")
    assert parsed.intent == "set_income"
    assert parsed.amount == 3000


def test_parse_set_committed() -> None:
    parsed = assert_parsed("comprometido 1800")
    assert parsed.intent == "set_committed"
    assert parsed.amount == 1800
