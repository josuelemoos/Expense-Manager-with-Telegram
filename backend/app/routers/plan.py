from typing import Annotated

from fastapi import APIRouter, Query

from app.routers.deps import SessionDep, UserIdDep
from app.routers.errors import service_error_to_http
from app.schemas.plan import (
    AllocationRuleRead,
    AllocationRuleUpsert,
    MonthlyPlanRead,
    MonthlyPlanUpsert,
    PlanProgress,
)
from app.services.exceptions import ServiceError
from app.services.plan_service import (
    get_monthly_plan_read,
    get_plan_progress,
    list_allocation_rules,
    upsert_allocation_rule,
    upsert_monthly_plan,
)


router = APIRouter(prefix="/plan", tags=["plan"])


@router.get("", response_model=MonthlyPlanRead)
def get_plan(
    session: SessionDep,
    user_id: UserIdDep,
    month: Annotated[int | None, Query(ge=1, le=12)] = None,
    year: Annotated[int | None, Query(ge=2000)] = None,
) -> MonthlyPlanRead:
    try:
        return get_monthly_plan_read(session, user_id, month, year)
    except ServiceError as error:
        raise service_error_to_http(error) from error


@router.post("", response_model=MonthlyPlanRead)
def post_plan(
    data: MonthlyPlanUpsert,
    session: SessionDep,
    user_id: UserIdDep,
) -> MonthlyPlanRead:
    try:
        return upsert_monthly_plan(session, user_id, data)
    except ServiceError as error:
        raise service_error_to_http(error) from error


@router.get("/allocations", response_model=list[AllocationRuleRead])
def get_allocations(session: SessionDep, user_id: UserIdDep) -> list[AllocationRuleRead]:
    return list_allocation_rules(session, user_id)


@router.post("/allocations", response_model=AllocationRuleRead)
def post_allocation(
    data: AllocationRuleUpsert,
    session: SessionDep,
    user_id: UserIdDep,
) -> AllocationRuleRead:
    try:
        return upsert_allocation_rule(session, user_id, data)
    except ServiceError as error:
        raise service_error_to_http(error) from error


@router.get("/progress", response_model=PlanProgress)
def get_progress(
    session: SessionDep,
    user_id: UserIdDep,
    month: Annotated[int | None, Query(ge=1, le=12)] = None,
    year: Annotated[int | None, Query(ge=2000)] = None,
) -> PlanProgress:
    try:
        return get_plan_progress(session, user_id, month, year)
    except ServiceError as error:
        raise service_error_to_http(error) from error
