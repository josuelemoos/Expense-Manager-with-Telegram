from typing import Annotated, Literal

from fastapi import APIRouter, Query, status

from app.routers.deps import SessionDep, UserIdDep
from app.routers.errors import service_error_to_http
from app.schemas.transaction import TransactionCreate, TransactionRead
from app.services.exceptions import ServiceError
from app.services.transaction_service import create_transaction, list_transactions


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def post_transaction(
    data: TransactionCreate,
    session: SessionDep,
    user_id: UserIdDep,
) -> TransactionRead:
    try:
        return create_transaction(session, user_id, data)
    except ServiceError as error:
        raise service_error_to_http(error) from error


@router.get("", response_model=list[TransactionRead])
def get_transactions(
    session: SessionDep,
    user_id: UserIdDep,
    month: Annotated[int | None, Query(ge=1, le=12)] = None,
    year: Annotated[int | None, Query(ge=2000)] = None,
    type_: Annotated[
        Literal["income", "expense", "transfer"] | None,
        Query(alias="type"),
    ] = None,
    category_id: int | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[TransactionRead]:
    try:
        return list_transactions(
            session=session,
            user_id=user_id,
            month=month,
            year=year,
            type_=type_,
            category_id=category_id,
            limit=limit,
            offset=offset,
        )
    except ServiceError as error:
        raise service_error_to_http(error) from error
