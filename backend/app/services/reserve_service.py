from decimal import Decimal

from sqlmodel import Session, select

from app.models import Reserve, Transaction
from app.schemas.reserve import ReserveCreate, ReserveDepositCreate
from app.services.account_service import get_account_or_default
from app.services.atomic import atomic_write
from app.services.category_service import find_category_by_name
from app.services.exceptions import NotFoundError, ValidationError
from app.utils.date_helpers import now_in_timezone


def list_reserves(session: Session, user_id: int) -> list[Reserve]:
    return list(
        session.exec(
            select(Reserve)
            .where(Reserve.user_id == user_id, Reserve.is_active == True)
            .order_by(Reserve.name),
        ).all(),
    )


def create_reserve(session: Session, user_id: int, data: ReserveCreate) -> Reserve:
    reserve = Reserve(
        user_id=user_id,
        name=data.name.strip(),
        goal_value=data.goal_value,
        description=data.description,
    )
    with atomic_write(session):
        session.add(reserve)
    session.refresh(reserve)
    return reserve


def get_reserve(session: Session, user_id: int, reserve_id: int) -> Reserve:
    reserve = session.exec(
        select(Reserve).where(
            Reserve.id == reserve_id,
            Reserve.user_id == user_id,
            Reserve.is_active == True,
        ),
    ).first()
    if not reserve:
        raise NotFoundError("Reserva nao encontrada.")
    return reserve


def progress_percentage(reserve: Reserve) -> Decimal | None:
    if not reserve.goal_value or reserve.goal_value == 0:
        return None
    percentage = (reserve.current_value / reserve.goal_value) * Decimal("100")
    return percentage.quantize(Decimal("0.01"))


def deposit_to_reserve(
    session: Session,
    user_id: int,
    reserve_id: int,
    data: ReserveDepositCreate,
) -> tuple[Reserve, Decimal, Decimal | None]:
    reserve = get_reserve(session, user_id, reserve_id)
    account = get_account_or_default(session, user_id, data.account_id)
    amount = data.amount.quantize(Decimal("0.01"))

    if account.current_balance < amount:
        raise ValidationError("Saldo insuficiente para aportar na reserva.")

    category = find_category_by_name(session, user_id, "Reservas", "expense")

    transaction = Transaction(
        user_id=user_id,
        account_id=account.id,
        category_id=category.id if category else None,
        type="expense",
        amount=amount,
        description=f"Aporte em {reserve.name}",
        date=now_in_timezone().date(),
        notes=data.notes,
        source="manual",
    )

    with atomic_write(session):
        reserve.current_value += amount
        account.current_balance -= amount
        session.add(account)
        session.add(reserve)
        session.add(transaction)
    session.refresh(reserve)
    session.refresh(account)
    return reserve, account.current_balance, progress_percentage(reserve)
