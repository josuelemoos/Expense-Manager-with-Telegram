from telegram.ext import Application, CommandHandler, MessageHandler, filters

from app.config import settings
from app.telegram.commands import (
    balance_command,
    categories_command,
    chart_command,
    effect_command,
    help_command,
    planning_command,
    reserves_command,
    start_command,
    statement_command,
    summary_command,
    text_message_handler,
)


_application: Application | None = None
_initialized = False


def build_application() -> Application:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN nao configurado.")

    application = Application.builder().token(settings.telegram_bot_token).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ajuda", help_command))
    application.add_handler(CommandHandler("saldo", balance_command))
    application.add_handler(CommandHandler("resumo", summary_command))
    application.add_handler(CommandHandler("reservas", reserves_command))
    application.add_handler(CommandHandler("categorias", categories_command))
    application.add_handler(CommandHandler("extrato", statement_command))
    application.add_handler(CommandHandler("grafico", chart_command))
    application.add_handler(CommandHandler("planejamento", planning_command))
    application.add_handler(CommandHandler("efeito", effect_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    return application


async def get_application() -> Application:
    global _application, _initialized

    if _application is None:
        _application = build_application()
    if not _initialized:
        await _application.initialize()
        _initialized = True
    return _application
