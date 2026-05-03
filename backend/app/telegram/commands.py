from decimal import Decimal
import logging

from sqlmodel import Session
from telegram import Update
from telegram.ext import ContextTypes

from app.config import settings
from app.database import engine
from app.models import Reserve
from app.schemas.plan import MonthlyPlanUpsert
from app.schemas.reserve import ReserveDepositCreate, ReserveDepositRead
from app.schemas.transaction import TransactionCreate
from app.services.category_service import find_category_by_name, list_categories
from app.services.chart_service import generate_bars_chart, generate_pie_chart
from app.services.exceptions import ServiceError, ValidationError
from app.services.plan_service import get_monthly_plan_read, get_plan_progress, upsert_monthly_plan
from app.services.reserve_service import deposit_to_reserve, list_reserves
from app.services.summary_service import get_balance_summary, get_monthly_summary
from app.services.transaction_service import (
    create_expense,
    create_income,
    list_recent_transactions,
)
from app.telegram.parser import ParseError, ParsedMessage, parse_message
from app.telegram.responses import (
    format_balance,
    format_categories,
    format_monthly_summary,
    format_parse_error,
    format_plan,
    format_plan_update,
    format_reserve_deposit,
    format_reserves,
    format_service_error,
    format_transaction_result,
    format_transactions,
    help_message,
    start_message,
)
from app.utils.date_helpers import now_in_timezone


UNAUTHORIZED_MESSAGE = (
    "Este chat nao esta autorizado para usar o FinTrack.\n\n"
    "Se este e o seu chat, configure DEFAULT_USER_TELEGRAM_CHAT_ID com o id correto."
)
logger = logging.getLogger(__name__)


def _chat_id(update: Update) -> int | None:
    return update.effective_chat.id if update.effective_chat else None


def _is_authorized(update: Update) -> bool:
    allowed_chat_id = settings.default_user_telegram_chat_id
    chat_id = _chat_id(update)
    return allowed_chat_id is None or chat_id == allowed_chat_id


async def _reply_text(update: Update, text: str) -> None:
    if update.effective_message:
        await update.effective_message.reply_text(text)


async def _reject_if_unauthorized(update: Update) -> bool:
    if _is_authorized(update):
        return False
    logger.warning("Unauthorized Telegram chat_id=%s", _chat_id(update))
    await _reply_text(update, UNAUTHORIZED_MESSAGE)
    return True


def _default_user_id() -> int:
    return settings.default_user_id


def _category_id_for(
    session: Session,
    user_id: int,
    category_name: str | None,
    type_: str,
) -> int | None:
    category = None
    if category_name:
        category = find_category_by_name(session, user_id, category_name, type_)
    if not category:
        category = find_category_by_name(session, user_id, "Outros", type_)
    return category.id if category else None


def _reserve_for_name(
    session: Session,
    user_id: int,
    reserve_name: str | None,
) -> Reserve:
    reserves = list_reserves(session, user_id)
    if not reserves:
        raise ValidationError("Nenhuma reserva ativa encontrada.")
    if reserve_name:
        normalized = reserve_name.lower()
        for reserve in reserves:
            if reserve.name.lower() == normalized:
                return reserve
    return reserves[0]


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _reject_if_unauthorized(update):
        return
    await _reply_text(update, start_message())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _reject_if_unauthorized(update):
        return
    await _reply_text(update, help_message())


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _reject_if_unauthorized(update):
        return
    with Session(engine) as session:
        await _reply_text(update, format_balance(get_balance_summary(session, _default_user_id())))


async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _reject_if_unauthorized(update):
        return
    with Session(engine) as session:
        await _reply_text(update, format_monthly_summary(get_monthly_summary(session, _default_user_id())))


async def reserves_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _reject_if_unauthorized(update):
        return
    with Session(engine) as session:
        await _reply_text(update, format_reserves(list_reserves(session, _default_user_id())))


async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _reject_if_unauthorized(update):
        return
    with Session(engine) as session:
        await _reply_text(update, format_categories(list_categories(session, _default_user_id())))


async def statement_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _reject_if_unauthorized(update):
        return
    with Session(engine) as session:
        await _reply_text(update, format_transactions(list_recent_transactions(session, _default_user_id(), 10)))


async def planning_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _reject_if_unauthorized(update):
        return
    with Session(engine) as session:
        await _reply_text(update, format_plan(get_plan_progress(session, _default_user_id())))


async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _reject_if_unauthorized(update):
        return
    chart_type = "bars" if context.args and context.args[0].lower() == "barras" else "pie"
    with Session(engine) as session:
        image = (
            generate_bars_chart(session, _default_user_id())
            if chart_type == "bars"
            else generate_pie_chart(session, _default_user_id())
        )
    if update.effective_message:
        await update.effective_message.reply_photo(photo=image)


def _current_plan_data(
    session: Session,
    user_id: int,
    expected_income: Decimal | None = None,
    committed_expenses: Decimal | None = None,
) -> MonthlyPlanUpsert:
    today = now_in_timezone().date()
    current = get_monthly_plan_read(session, user_id, today.month, today.year)
    expected = expected_income if expected_income is not None else current.expected_income
    committed = (
        committed_expenses
        if committed_expenses is not None
        else current.committed_expenses
    )
    if expected < committed:
        expected = committed
    return MonthlyPlanUpsert(
        month=today.month,
        year=today.year,
        expected_income=expected,
        committed_expenses=committed,
        notes=current.notes,
    )


async def handle_parsed_message(update: Update, parsed: ParsedMessage) -> None:
    user_id = _default_user_id()
    with Session(engine) as session:
        if parsed.intent == "query_balance":
            await _reply_text(update, format_balance(get_balance_summary(session, user_id)))
            return
        if parsed.intent == "query_summary":
            await _reply_text(update, format_monthly_summary(get_monthly_summary(session, user_id)))
            return
        if parsed.intent == "query_reserves":
            await _reply_text(update, format_reserves(list_reserves(session, user_id)))
            return
        if parsed.intent == "query_plan":
            await _reply_text(update, format_plan(get_plan_progress(session, user_id)))
            return
        if parsed.intent in {"chart_pie", "chart_bars"}:
            image = (
                generate_bars_chart(session, user_id)
                if parsed.intent == "chart_bars"
                else generate_pie_chart(session, user_id)
            )
            if update.effective_message:
                await update.effective_message.reply_photo(photo=image)
            return
        if parsed.intent == "set_income" and parsed.amount is not None:
            plan = upsert_monthly_plan(
                session,
                user_id,
                _current_plan_data(session, user_id, expected_income=parsed.amount),
            )
            await _reply_text(update, format_plan_update(plan))
            return
        if parsed.intent == "set_committed" and parsed.amount is not None:
            plan = upsert_monthly_plan(
                session,
                user_id,
                _current_plan_data(session, user_id, committed_expenses=parsed.amount),
            )
            await _reply_text(update, format_plan_update(plan))
            return
        if parsed.intent == "reserve_deposit" and parsed.amount is not None:
            reserve = _reserve_for_name(session, user_id, parsed.reserve_name)
            reserve_obj, account_balance, progress = deposit_to_reserve(
                session,
                user_id,
                reserve.id,
                ReserveDepositCreate(amount=parsed.amount),
            )
            await _reply_text(
                update,
                format_reserve_deposit(
                    ReserveDepositRead.model_validate(
                        {
                            "reserve": reserve_obj,
                            "account_balance": account_balance,
                            "progress_percentage": progress,
                        },
                    ),
                ),
            )
            return
        if parsed.intent in {"expense", "income"} and parsed.amount is not None:
            type_ = "income" if parsed.intent == "income" else "expense"
            category_id = _category_id_for(session, user_id, parsed.suggested_category, type_)
            payload = TransactionCreate(
                type=type_,
                amount=parsed.amount,
                description=parsed.description or parsed.raw_text,
                category_id=category_id,
                source="telegram",
            )
            result = create_income(session, user_id, payload) if type_ == "income" else create_expense(session, user_id, payload)
            await _reply_text(update, format_transaction_result(result))
            return

    await _reply_text(update, "Nao consegui processar essa mensagem.")


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _reject_if_unauthorized(update):
        return
    text = update.effective_message.text if update.effective_message else ""
    parsed = parse_message(text or "")
    if isinstance(parsed, ParseError):
        await _reply_text(update, format_parse_error(parsed))
        return
    try:
        await handle_parsed_message(update, parsed)
    except ServiceError as error:
        await _reply_text(update, format_service_error(error.detail))
    except Exception:
        logger.exception("Erro inesperado ao processar mensagem do Telegram")
        await _reply_text(
            update,
            "Nao consegui processar agora. Tente novamente em instantes.",
        )
