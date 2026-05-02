"""initial schema

Revision ID: 20260502_0001
Revises:
Create Date: 2026-05-02 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "20260502_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("telegram_chat_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("telegram_chat_id"),
    )

    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type", sa.String(length=30), nullable=False),
        sa.Column("initial_balance", sa.Numeric(precision=12, scale=2), server_default=sa.text("0"), nullable=False),
        sa.Column("current_balance", sa.Numeric(precision=12, scale=2), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.CheckConstraint("type IN ('wallet', 'bank', 'savings', 'credit')", name="ck_accounts_type"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type", sa.String(length=10), nullable=False),
        sa.Column("monthly_limit", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("color", sa.String(length=7), nullable=True),
        sa.Column("icon", sa.String(length=50), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.CheckConstraint("type IN ('expense', 'income')", name="ck_categories_type"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "reserves",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("current_value", sa.Numeric(precision=12, scale=2), server_default=sa.text("0"), nullable=False),
        sa.Column("goal_value", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.CheckConstraint("current_value >= 0", name="ck_reserves_current_non_negative"),
        sa.CheckConstraint("goal_value IS NULL OR goal_value >= 0", name="ck_reserves_goal_non_negative"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "allocation_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("percentage", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("emoji", sa.String(length=10), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.CheckConstraint("percentage >= 0 AND percentage <= 100", name="ck_allocation_rules_percentage_range"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "budgets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("limit_value", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.CheckConstraint("limit_value >= 0", name="ck_budgets_limit_non_negative"),
        sa.CheckConstraint("month BETWEEN 1 AND 12", name="ck_budgets_month"),
        sa.CheckConstraint("year >= 2000", name="ck_budgets_year"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "category_id", "month", "year", name="uq_budgets_user_category_month_year"),
    )

    op.create_table(
        "monthly_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("expected_income", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("committed_expenses", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("committed_expenses <= expected_income", name="ck_monthly_plans_committed_lte_expected"),
        sa.CheckConstraint("committed_expenses >= 0", name="ck_monthly_plans_committed_non_negative"),
        sa.CheckConstraint("expected_income >= 0", name="ck_monthly_plans_expected_non_negative"),
        sa.CheckConstraint("month BETWEEN 1 AND 12", name="ck_monthly_plans_month"),
        sa.CheckConstraint("year >= 2000", name="ck_monthly_plans_year"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "month", "year", name="uq_monthly_plans_user_month_year"),
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(length=15), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("date", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("source", sa.String(length=20), server_default=sa.text("'manual'"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        sa.CheckConstraint("source IN ('manual', 'telegram', 'import')", name="ck_transactions_source"),
        sa.CheckConstraint("type IN ('income', 'expense', 'transfer')", name="ck_transactions_type"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("transactions")
    op.drop_table("monthly_plans")
    op.drop_table("budgets")
    op.drop_table("allocation_rules")
    op.drop_table("reserves")
    op.drop_table("categories")
    op.drop_table("accounts")
    op.drop_table("users")
