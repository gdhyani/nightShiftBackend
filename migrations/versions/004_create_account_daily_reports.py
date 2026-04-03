"""create account, daily_reports, skill_versions tables

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("balance", sa.Float(), nullable=False, server_default=sa.text("10000.0")),
        sa.Column("equity", sa.Float(), nullable=False, server_default=sa.text("10000.0")),
        sa.Column("margin_used", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("daily_loss_limit", sa.Float(), nullable=False, server_default=sa.text("500.0")),
        sa.Column("max_drawdown", sa.Float(), nullable=False, server_default=sa.text("2000.0")),
        sa.Column("max_position_size", sa.Float(), nullable=False, server_default=sa.text("1.0")),
        sa.Column("risk_per_trade", sa.Float(), nullable=False, server_default=sa.text("0.02")),
        sa.Column("settings", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "daily_reports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("date", sa.String(length=10), nullable=False, unique=True),
        sa.Column("summary", sa.String(length=2000), nullable=False),
        sa.Column("trades_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("wins", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("losses", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_pnl", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "skill_versions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("skill_path", sa.String(length=200), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("changed_by", sa.String(length=100), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("skill_versions")
    op.drop_table("daily_reports")
    op.drop_table("accounts")
