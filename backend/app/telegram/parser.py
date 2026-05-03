from dataclasses import dataclass
from datetime import date as PyDate, timedelta
from decimal import Decimal
import re
import unicodedata
from typing import Literal


Intent = Literal[
    "expense",
    "income",
    "reserve_deposit",
    "query_balance",
    "query_summary",
    "query_reserves",
    "query_plan",
    "chart_pie",
    "chart_bars",
    "simulate_expense_effect",
    "set_income",
    "set_committed",
    "unknown",
]

ParseErrorType = Literal["no_amount", "no_context", "ambiguous", "unknown_intent"]


@dataclass(frozen=True)
class ParsedMessage:
    intent: Intent
    amount: Decimal | None = None
    description: str | None = None
    suggested_category: str | None = None
    date: PyDate | None = None
    reserve_name: str | None = None
    raw_text: str = ""
    confidence: float = 0.0


@dataclass(frozen=True)
class ParseError:
    error_type: ParseErrorType
    message: str
    suggestion: str


def _norm(value: str) -> str:
    ascii_text = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    return re.sub(r"\s+", " ", ascii_text.lower().strip())


CATEGORY_ALIASES = {
    "mercado": "Alimenta\u00e7\u00e3o",
    "supermercado": "Alimenta\u00e7\u00e3o",
    "padaria": "Alimenta\u00e7\u00e3o",
    "ifood": "Alimenta\u00e7\u00e3o",
    "pizza": "Alimenta\u00e7\u00e3o",
    "restaurante": "Alimenta\u00e7\u00e3o",
    "lanche": "Alimenta\u00e7\u00e3o",
    "almoco": "Alimenta\u00e7\u00e3o",
    "jantar": "Alimenta\u00e7\u00e3o",
    "uber": "Transporte",
    "onibus": "Transporte",
    "gasolina": "Transporte",
    "combustivel": "Transporte",
    "99": "Transporte",
    "taxi": "Transporte",
    "metro": "Transporte",
    "farmacia": "Sa\u00fade",
    "remedio": "Sa\u00fade",
    "medico": "Sa\u00fade",
    "consulta": "Sa\u00fade",
    "academia": "Sa\u00fade",
    "luz": "Contas fixas",
    "agua": "Contas fixas",
    "internet": "Contas fixas",
    "aluguel": "Moradia",
    "cinema": "Lazer",
    "salario": "Sal\u00e1rio",
    "freela": "Freelance",
    "freelance": "Freelance",
}

INCOME_WORDS = {"recebi", "salario", "freela", "freelance"}
RESERVE_WORDS = {"guardei", "guardar", "reserva"}
EXPENSE_CONTEXT_WORDS = {"gastei", "comprei", "paguei", "mercado", "uber", "ifood"}
AMOUNT_RE = re.compile(r"(?<!\d)(\d+(?:[.,]\d{1,2})?)(?!\d)")
DAY_RE = re.compile(r"\bdia\s+(\d{1,2})\b")


def _extract_amount(text: str) -> Decimal | None:
    match = AMOUNT_RE.search(text)
    if not match:
        return None
    return Decimal(match.group(1).replace(",", ".")).quantize(Decimal("0.01"))


def _text_without_amount(text: str) -> str:
    return AMOUNT_RE.sub("", text).strip()


def _only_amount(normalized: str) -> bool:
    return bool(AMOUNT_RE.fullmatch(normalized))


def _suggest_category(normalized: str, default: str) -> str:
    for alias, category in CATEGORY_ALIASES.items():
        if re.search(rf"(^|\s){re.escape(alias)}($|\s)", normalized):
            return category
    return default


def _description(raw: str) -> str:
    cleaned = _text_without_amount(raw)
    cleaned = re.sub(
        r"\b(gastei|recebi|guardei|definir renda|comprometido|no|na|em|de)\b",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned.capitalize() if cleaned else raw.strip()


def _extract_effect_date(normalized: str) -> PyDate | None:
    from app.utils.date_helpers import now_in_timezone

    today = now_in_timezone().date()
    if re.search(r"(^|\s)hoje($|\s)", normalized):
        return today
    if re.search(r"(^|\s)amanha($|\s)", normalized):
        return today + timedelta(days=1)

    day_match = DAY_RE.search(normalized)
    if day_match:
        day = int(day_match.group(1))
        try:
            return PyDate(today.year, today.month, day)
        except ValueError:
            return None

    return None


def _effect_description(raw: str) -> str:
    cleaned = _text_without_amount(raw)
    cleaned = re.sub(r"(^|\s)/efeito($|\s)", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(
        r"\b(efeito|reais|real|hoje|amanha|amanh[aã]|dia\s+\d{1,2}|no|na|em|de)\b",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned.capitalize() if cleaned else raw.strip()


def parse_message(text: str) -> ParsedMessage | ParseError:
    raw = text.strip()
    normalized = _norm(raw)
    if not normalized:
        return ParseError(
            error_type="no_context",
            message="Nao consegui entender a mensagem.",
            suggestion="Tente: mercado 45",
        )

    if normalized in {"/saldo", "quanto tenho?", "quanto tenho"}:
        return ParsedMessage("query_balance", raw_text=raw, confidence=1.0)
    if normalized in {"/resumo", "como estou esse mes?", "como estou esse mes"}:
        return ParsedMessage("query_summary", raw_text=raw, confidence=1.0)
    if normalized == "/reservas":
        return ParsedMessage("query_reserves", raw_text=raw, confidence=1.0)
    if normalized == "/planejamento":
        return ParsedMessage("query_plan", raw_text=raw, confidence=1.0)
    if normalized.startswith("/grafico barras") or "grafico barras" in normalized:
        return ParsedMessage("chart_bars", raw_text=raw, confidence=1.0)
    if normalized.startswith("/grafico") or normalized == "grafico do mes":
        return ParsedMessage("chart_pie", raw_text=raw, confidence=1.0)

    amount = _extract_amount(normalized)
    if normalized.startswith("/efeito") or normalized.startswith("efeito "):
        if amount is None:
            return ParseError(
                "no_amount",
                "Nao consegui identificar o valor da simulacao.",
                "Tente: /efeito pizza de 42 reais hoje",
            )
        return ParsedMessage(
            "simulate_expense_effect",
            amount=amount,
            description=_effect_description(raw),
            suggested_category=_suggest_category(normalized, "Outros"),
            date=_extract_effect_date(normalized),
            raw_text=raw,
            confidence=0.94,
        )
    if normalized.startswith("definir renda"):
        if amount is None:
            return ParseError("no_amount", "Nao consegui identificar a renda.", "Tente: definir renda 3000")
        return ParsedMessage("set_income", amount=amount, raw_text=raw, confidence=0.95)
    if normalized.startswith("comprometido"):
        if amount is None:
            return ParseError("no_amount", "Nao consegui identificar o comprometido.", "Tente: comprometido 1800")
        return ParsedMessage("set_committed", amount=amount, raw_text=raw, confidence=0.95)

    if amount is None:
        if any(word in normalized for word in EXPENSE_CONTEXT_WORDS | INCOME_WORDS | RESERVE_WORDS):
            return ParseError(
                "no_amount",
                "Nao consegui identificar o valor.",
                "Tente: mercado 45",
            )
        return ParseError(
            "unknown_intent",
            "Nao consegui identificar a intencao.",
            "Tente: mercado 45, recebi 1500 ou /saldo",
        )

    if _only_amount(normalized):
        return ParseError(
            "ambiguous",
            f"Voce quer registrar R$ {amount} como despesa ou receita?",
            "Responda com uma descricao, por exemplo: mercado 45",
        )

    if any(word in normalized for word in RESERVE_WORDS):
        reserve_name = "Viagem" if "viagem" in normalized else None
        return ParsedMessage(
            "reserve_deposit",
            amount=amount,
            description=_description(raw),
            reserve_name=reserve_name,
            raw_text=raw,
            confidence=0.92,
        )

    if any(word in normalized for word in INCOME_WORDS):
        return ParsedMessage(
            "income",
            amount=amount,
            description=_description(raw),
            suggested_category=_suggest_category(normalized, "Outros"),
            raw_text=raw,
            confidence=0.88,
        )

    return ParsedMessage(
        "expense",
        amount=amount,
        description=_description(raw),
        suggested_category=_suggest_category(normalized, "Outros"),
        raw_text=raw,
        confidence=0.82,
    )
