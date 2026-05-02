from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import settings


def now_in_timezone() -> datetime:
    return datetime.now(ZoneInfo(settings.timezone))
