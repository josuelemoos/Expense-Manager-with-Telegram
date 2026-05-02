from decimal import Decimal

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app import models
from app.models import Account, AllocationRule, Category, Reserve, User


USER_ID = 1


@pytest.fixture
def session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def basic_data(session: Session) -> dict[str, object]:
    user = User(
        id=USER_ID,
        name="Usuario Teste",
        email="teste@example.com",
        password_hash="hash",
    )
    account = Account(
        user_id=USER_ID,
        name="Conta Principal",
        type="bank",
        initial_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00"),
        is_default=True,
    )
    food = Category(
        user_id=USER_ID,
        name="Alimentacao",
        type="expense",
        monthly_limit=Decimal("500.00"),
    )
    leisure = Category(
        user_id=USER_ID,
        name="Lazer",
        type="expense",
    )
    reserve_category = Category(
        user_id=USER_ID,
        name="Reservas",
        type="expense",
    )
    salary = Category(
        user_id=USER_ID,
        name="Salario",
        type="income",
    )
    reserve = Reserve(
        user_id=USER_ID,
        name="Emergencia",
        current_value=Decimal("0.00"),
        goal_value=Decimal("6000.00"),
    )
    leisure_rule = AllocationRule(
        user_id=USER_ID,
        name="Lazer",
        percentage=Decimal("20.00"),
        category_id=None,
        emoji="L",
        sort_order=1,
    )
    reserve_rule = AllocationRule(
        user_id=USER_ID,
        name="Reserva",
        percentage=Decimal("20.00"),
        category_id=None,
        emoji="R",
        sort_order=2,
    )

    session.add(user)
    session.add(account)
    session.add(food)
    session.add(leisure)
    session.add(reserve_category)
    session.add(salary)
    session.add(reserve)
    session.add(leisure_rule)
    session.add(reserve_rule)
    session.commit()

    session.refresh(account)
    session.refresh(food)
    session.refresh(leisure)
    session.refresh(reserve_category)
    session.refresh(salary)
    session.refresh(reserve)
    session.refresh(leisure_rule)
    session.refresh(reserve_rule)
    leisure_rule.category_id = leisure.id
    reserve_rule.category_id = reserve_category.id
    session.add(leisure_rule)
    session.add(reserve_rule)
    session.commit()
    session.refresh(leisure_rule)
    session.refresh(reserve_rule)

    return {
        "user": user,
        "account": account,
        "food": food,
        "leisure": leisure,
        "reserve_category": reserve_category,
        "salary": salary,
        "reserve": reserve,
        "leisure_rule": leisure_rule,
        "reserve_rule": reserve_rule,
    }
