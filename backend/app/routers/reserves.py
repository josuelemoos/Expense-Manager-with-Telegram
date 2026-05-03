from typing import Annotated

from fastapi import APIRouter, Path, status

from app.routers.deps import SessionDep, UserIdDep
from app.routers.errors import service_error_to_http
from app.schemas.reserve import (
    ReserveCreate,
    ReserveDepositCreate,
    ReserveDepositRead,
    ReserveRead,
)
from app.services.exceptions import ServiceError
from app.services.reserve_service import create_reserve, deposit_to_reserve, list_reserves


router = APIRouter(prefix="/reserves", tags=["reserves"])


@router.get("", response_model=list[ReserveRead])
def get_reserves(session: SessionDep, user_id: UserIdDep) -> list[ReserveRead]:
    return list_reserves(session, user_id)


@router.post("", response_model=ReserveRead, status_code=status.HTTP_201_CREATED)
def post_reserve(
    data: ReserveCreate,
    session: SessionDep,
    user_id: UserIdDep,
) -> ReserveRead:
    return create_reserve(session, user_id, data)


@router.post("/{reserve_id}/deposit", response_model=ReserveDepositRead)
def post_reserve_deposit(
    reserve_id: Annotated[int, Path(gt=0)],
    data: ReserveDepositCreate,
    session: SessionDep,
    user_id: UserIdDep,
) -> ReserveDepositRead:
    try:
        reserve, account_balance, progress = deposit_to_reserve(
            session,
            user_id,
            reserve_id,
            data,
        )
    except ServiceError as error:
        raise service_error_to_http(error) from error

    return ReserveDepositRead(
        reserve=ReserveRead.model_validate(reserve),
        account_balance=account_balance,
        progress_percentage=progress,
    )
