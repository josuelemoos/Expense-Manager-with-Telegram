from datetime import timedelta
from decimal import Decimal
import secrets

from app.schemas.reset import PendingReset
from app.services.reset_service import validate_reset_balance
from app.utils.date_helpers import now_in_timezone


RESET_CONFIRMATION_TTL_MINUTES = 10
_pending_resets: dict[int, PendingReset] = {}


def create_pending_reset(
    chat_id: int,
    user_id: int,
    initial_balance: Decimal | None = None,
) -> PendingReset:
    balance = validate_reset_balance(initial_balance)
    code = f"{secrets.randbelow(900000) + 100000}"
    pending = PendingReset(
        chat_id=chat_id,
        user_id=user_id,
        confirmation_code=code,
        initial_balance=balance,
        expires_at=now_in_timezone() + timedelta(minutes=RESET_CONFIRMATION_TTL_MINUTES),
    )
    _pending_resets[chat_id] = pending
    return pending


def consume_pending_reset(chat_id: int, confirmation_code: str) -> PendingReset | None:
    pending = _pending_resets.get(chat_id)
    if not pending:
        return None
    if pending.expires_at < now_in_timezone():
        _pending_resets.pop(chat_id, None)
        return None
    if pending.confirmation_code != confirmation_code:
        return None
    return _pending_resets.pop(chat_id)


def clear_pending_resets() -> None:
    _pending_resets.clear()
