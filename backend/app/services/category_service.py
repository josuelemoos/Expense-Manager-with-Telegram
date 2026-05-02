from typing import Literal

from sqlmodel import Session, select

from app.models import Category
from app.services.exceptions import NotFoundError, ValidationError


def list_categories(
    session: Session,
    user_id: int,
    type_: Literal["expense", "income"] | None = None,
) -> list[Category]:
    statement = select(Category).where(
        Category.user_id == user_id,
        Category.is_active == True,
    )
    if type_:
        statement = statement.where(Category.type == type_)
    return list(session.exec(statement.order_by(Category.type, Category.name)).all())


def get_category(session: Session, user_id: int, category_id: int) -> Category:
    category = session.exec(
        select(Category).where(
            Category.id == category_id,
            Category.user_id == user_id,
            Category.is_active == True,
        ),
    ).first()
    if not category:
        raise NotFoundError("Categoria nao encontrada.")
    return category


def get_category_or_none(
    session: Session,
    user_id: int,
    category_id: int | None,
) -> Category | None:
    if category_id is None:
        return None
    return get_category(session, user_id, category_id)


def validate_category_for_transaction(
    category: Category | None,
    transaction_type: Literal["income", "expense"],
) -> None:
    if category and category.type != transaction_type:
        raise ValidationError("Categoria incompativel com o tipo da transacao.")


def find_category_by_name(
    session: Session,
    user_id: int,
    name: str,
    type_: Literal["expense", "income"],
) -> Category | None:
    return session.exec(
        select(Category).where(
            Category.user_id == user_id,
            Category.name == name,
            Category.type == type_,
            Category.is_active == True,
        ),
    ).first()
