from collections.abc import Iterator
from contextlib import contextmanager

from sqlmodel import Session


@contextmanager
def atomic_write(session: Session) -> Iterator[None]:
    try:
        yield
        session.commit()
    except Exception:
        session.rollback()
        raise
