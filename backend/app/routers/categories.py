from typing import Annotated, Literal

from fastapi import APIRouter, Query

from app.routers.deps import SessionDep, UserIdDep
from app.schemas.category import CategoryRead
from app.services.category_service import list_categories


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def get_categories(
    session: SessionDep,
    user_id: UserIdDep,
    type_: Annotated[Literal["expense", "income"] | None, Query(alias="type")] = None,
) -> list[CategoryRead]:
    return list_categories(session, user_id, type_)
