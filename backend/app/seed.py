from decimal import Decimal

from sqlalchemy import text
from sqlmodel import Session, select

from app.config import settings
from app.database import engine
from app.models import Account, AllocationRule, Category, Reserve, User


def money(value: str | int | float | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def get_or_create_user(session: Session) -> User:
    user = session.get(User, settings.default_user_id)
    if user:
        if settings.default_user_telegram_chat_id and not user.telegram_chat_id:
            user.telegram_chat_id = settings.default_user_telegram_chat_id
            session.add(user)
        return user

    user = User(
        id=settings.default_user_id,
        name="Usuario MVP",
        email="usuario@example.com",
        password_hash="change-this-after-auth-is-implemented",
        telegram_chat_id=settings.default_user_telegram_chat_id,
    )
    session.add(user)
    session.flush()
    return user


def seed_accounts(session: Session, user_id: int) -> None:
    accounts = [
        {
            "name": "Conta Principal",
            "type": "bank",
            "initial_balance": money("0"),
            "current_balance": money("0"),
            "is_default": True,
        },
        {
            "name": "Carteira",
            "type": "wallet",
            "initial_balance": money("0"),
            "current_balance": money("0"),
            "is_default": False,
        },
    ]

    for data in accounts:
        existing = session.exec(
            select(Account).where(
                Account.user_id == user_id,
                Account.name == data["name"],
            ),
        ).first()
        if not existing:
            session.add(Account(user_id=user_id, **data))


def seed_categories(session: Session, user_id: int) -> dict[tuple[str, str], Category]:
    categories = [
        ("Alimenta\u00e7\u00e3o", "expense", "#6366f1", "utensils"),
        ("Transporte", "expense", "#f59e0b", "car"),
        ("Moradia", "expense", "#10b981", "home"),
        ("Sa\u00fade", "expense", "#ef4444", "heart-pulse"),
        ("Lazer", "expense", "#8b5cf6", "gamepad-2"),
        ("Educa\u00e7\u00e3o", "expense", "#3b82f6", "graduation-cap"),
        ("Roupas", "expense", "#ec4899", "shirt"),
        ("Contas fixas", "expense", "#64748b", "receipt"),
        ("Outros", "expense", "#f97316", "circle-help"),
        ("Reservas", "expense", "#14b8a6", "piggy-bank"),
        ("Sal\u00e1rio", "income", "#22c55e", "wallet"),
        ("Freelance", "income", "#06b6d4", "briefcase"),
        ("Investimentos", "income", "#84cc16", "trending-up"),
        ("Outros", "income", "#94a3b8", "circle-help"),
    ]

    by_key: dict[tuple[str, str], Category] = {}
    for name, type_, color, icon in categories:
        category = session.exec(
            select(Category).where(
                Category.user_id == user_id,
                Category.name == name,
                Category.type == type_,
            ),
        ).first()
        if not category:
            category = Category(
                user_id=user_id,
                name=name,
                type=type_,
                color=color,
                icon=icon,
            )
            session.add(category)
            session.flush()
        by_key[(name, type_)] = category
    return by_key


def seed_reserves(session: Session, user_id: int) -> None:
    emergency_goal = money(settings.default_monthly_income) * Decimal("6")
    reserves = [
        ("Reserva de Emerg\u00eancia", emergency_goal, "Reserva principal para imprevistos."),
        ("Viagem", None, None),
        ("Outros", None, None),
    ]

    for name, goal_value, description in reserves:
        existing = session.exec(
            select(Reserve).where(
                Reserve.user_id == user_id,
                Reserve.name == name,
            ),
        ).first()
        if not existing:
            session.add(
                Reserve(
                    user_id=user_id,
                    name=name,
                    goal_value=goal_value,
                    description=description,
                ),
            )


def seed_allocation_rules(
    session: Session,
    user_id: int,
    categories: dict[tuple[str, str], Category],
) -> None:
    rules = [
        ("Investimentos", money("40"), None, "\U0001f4c8", 1),
        ("Lazer", money("20"), categories.get(("Lazer", "expense")), "\U0001f389", 2),
        ("Reserva", money("20"), categories.get(("Reservas", "expense")), "\U0001f6e1\ufe0f", 3),
        ("Outros", money("20"), categories.get(("Outros", "expense")), "\U0001f4e6", 4),
    ]

    for name, percentage, category, emoji, sort_order in rules:
        existing = session.exec(
            select(AllocationRule).where(
                AllocationRule.user_id == user_id,
                AllocationRule.name == name,
            ),
        ).first()
        if not existing:
            session.add(
                AllocationRule(
                    user_id=user_id,
                    name=name,
                    percentage=percentage,
                    category_id=category.id if category else None,
                    emoji=emoji,
                    sort_order=sort_order,
                ),
            )


def sync_postgres_sequences(session: Session) -> None:
    bind = session.get_bind()
    if bind.dialect.name != "postgresql":
        return

    tables = ["users", "accounts", "categories", "reserves", "allocation_rules"]
    for table in tables:
        session.execute(
            text(
                f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                f"GREATEST((SELECT COALESCE(MAX(id), 1) FROM {table}), 1), true)",
            ),
        )


def run_seed() -> None:
    with Session(engine) as session:
        user = get_or_create_user(session)
        seed_accounts(session, user.id)
        categories = seed_categories(session, user.id)
        seed_reserves(session, user.id)
        seed_allocation_rules(session, user.id, categories)
        sync_postgres_sequences(session)
        session.commit()


if __name__ == "__main__":
    run_seed()
    print("Seed completed.")
