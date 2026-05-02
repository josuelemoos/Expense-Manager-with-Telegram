from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.config import settings
from app.database import get_session


SessionDep = Annotated[Session, Depends(get_session)]


def get_default_user_id() -> int:
    return settings.default_user_id


UserIdDep = Annotated[int, Depends(get_default_user_id)]
