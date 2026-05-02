from typing import Annotated

from fastapi import APIRouter, Query, Response

from app.routers.deps import SessionDep, UserIdDep
from app.routers.errors import service_error_to_http
from app.services.chart_service import generate_bars_chart, generate_pie_chart
from app.services.exceptions import ServiceError


router = APIRouter(prefix="/charts", tags=["charts"])


@router.get("/pie")
def pie_chart(
    session: SessionDep,
    user_id: UserIdDep,
    month: Annotated[int | None, Query(ge=1, le=12)] = None,
    year: Annotated[int | None, Query(ge=2000)] = None,
) -> Response:
    try:
        image = generate_pie_chart(session, user_id, month, year)
        return Response(content=image.getvalue(), media_type="image/png")
    except ServiceError as error:
        raise service_error_to_http(error) from error


@router.get("/bars")
def bars_chart(
    session: SessionDep,
    user_id: UserIdDep,
    months: Annotated[int, Query(ge=1, le=24)] = 6,
) -> Response:
    try:
        image = generate_bars_chart(session, user_id, months)
        return Response(content=image.getvalue(), media_type="image/png")
    except ServiceError as error:
        raise service_error_to_http(error) from error
