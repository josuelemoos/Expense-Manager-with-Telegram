from fastapi import APIRouter

from app.routers.deps import SessionDep, UserIdDep
from app.schemas.account import AccountBalanceItem, AccountBalanceSummary, AccountRead
from app.services.account_service import list_accounts, total_balance


router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountRead])
def get_accounts(session: SessionDep, user_id: UserIdDep) -> list[AccountRead]:
    return list_accounts(session, user_id)


@router.get("/balance", response_model=AccountBalanceSummary)
def get_balance(session: SessionDep, user_id: UserIdDep) -> AccountBalanceSummary:
    accounts = list_accounts(session, user_id)
    return AccountBalanceSummary(
        total=total_balance(accounts),
        accounts=[AccountBalanceItem.model_validate(account) for account in accounts],
    )
