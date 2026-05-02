from typing import Annotated

from fastapi import APIRouter, Query

from app.routers.deps import SessionDep, UserIdDep
from app.routers.errors import service_error_to_http
from app.schemas.summary import DashboardSummary, MonthlySummary
from app.services.exceptions import ServiceError
from app.services.summary_service import get_dashboard_summary, get_monthly_summary


router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/monthly", response_model=MonthlySummary)
def monthly_summary(
    session: SessionDep,
    user_id: UserIdDep,
    month: Annotated[int | None, Query(ge=1, le=12)] = None,
    year: Annotated[int | None, Query(ge=2000)] = None,
) -> MonthlySummary:
    try:
        return get_monthly_summary(session, user_id, month, year)
    except ServiceError as error:
        raise service_error_to_http(error) from error


@router.get("/dashboard", response_model=DashboardSummary)
def dashboard_summary(
    session: SessionDep,
    user_id: UserIdDep,
    month: Annotated[int | None, Query(ge=1, le=12)] = None,
    year: Annotated[int | None, Query(ge=2000)] = None,
) -> DashboardSummary:
    try:
        return get_dashboard_summary(session, user_id, month, year)
    except ServiceError as error:
        raise service_error_to_http(error) from error
