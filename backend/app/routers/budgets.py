from typing import Annotated

from fastapi import APIRouter, Query

from app.routers.deps import SessionDep, UserIdDep
from app.routers.errors import service_error_to_http
from app.schemas.budget import BudgetProgress, BudgetRead, BudgetUpsert
from app.services.budget_service import list_budget_progress, list_budgets, upsert_budget
from app.services.exceptions import ServiceError


router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("", response_model=list[BudgetRead])
def get_budgets(
    session: SessionDep,
    user_id: UserIdDep,
    month: Annotated[int | None, Query(ge=1, le=12)] = None,
    year: Annotated[int | None, Query(ge=2000)] = None,
) -> list[BudgetRead]:
    return list_budgets(session, user_id, month, year)


@router.post("", response_model=BudgetRead)
def post_budget(
    data: BudgetUpsert,
    session: SessionDep,
    user_id: UserIdDep,
) -> BudgetRead:
    try:
        budget = upsert_budget(
            session=session,
            user_id=user_id,
            category_id=data.category_id,
            month=data.month,
            year=data.year,
            limit_value=data.limit_value,
        )
        return BudgetRead.model_validate(budget)
    except ServiceError as error:
        raise service_error_to_http(error) from error


@router.get("/progress", response_model=list[BudgetProgress])
def get_progress(
    session: SessionDep,
    user_id: UserIdDep,
    month: Annotated[int | None, Query(ge=1, le=12)] = None,
    year: Annotated[int | None, Query(ge=2000)] = None,
) -> list[BudgetProgress]:
    try:
        return list_budget_progress(session, user_id, month, year)
    except ServiceError as error:
        raise service_error_to_http(error) from error
