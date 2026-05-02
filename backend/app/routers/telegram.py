from typing import Any

from fastapi import APIRouter, HTTPException
from telegram import Update

from app.config import settings
from app.telegram.bot import get_application


router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook")
async def telegram_webhook(payload: dict[str, Any]) -> dict[str, bool]:
    application = await get_application()
    update = Update.de_json(payload, application.bot)
    if update is None:
        raise HTTPException(status_code=400, detail="Update invalido.")
    await application.process_update(update)
    return {"ok": True}


@router.post("/setup")
async def telegram_setup() -> dict[str, str]:
    if not settings.telegram_webhook_url:
        raise HTTPException(status_code=400, detail="TELEGRAM_WEBHOOK_URL nao configurada.")
    application = await get_application()
    await application.bot.set_webhook(settings.telegram_webhook_url)
    return {"webhook_url": settings.telegram_webhook_url}
