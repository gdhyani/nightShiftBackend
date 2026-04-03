"""add user_trading_configs and instruments tables

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-04-01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_trading_configs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(50), unique=True, nullable=False, server_default="default"),
        sa.Column("upstox_client_id", sa.String(100), nullable=False, server_default=""),
        sa.Column("upstox_client_secret_enc", sa.Text(), nullable=False, server_default=""),
        sa.Column("daily_token_enc", sa.Text(), nullable=False, server_default=""),
        sa.Column("daily_token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sandbox_token_enc", sa.Text(), nullable=False, server_default=""),
        sa.Column("sandbox_token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("default_mode", sa.String(10), nullable=False, server_default="paper"),
        sa.Column("notifier_url", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "instruments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("instrument_key", sa.String(100), unique=True, nullable=False),
        sa.Column("symbol", sa.String(50), nullable=False),
        sa.Column("name", sa.String(200), nullable=False, server_default=""),
        sa.Column("exchange", sa.String(10), nullable=False, server_default=""),
        sa.Column("segment", sa.String(10), nullable=False, server_default=""),
        sa.Column("isin", sa.String(20), nullable=True),
        sa.Column("lot_size", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("tick_size", sa.Float(), nullable=False, server_default="0.05"),
        sa.Column("instrument_type", sa.String(10), nullable=True),
        sa.Column("expiry", sa.Date(), nullable=True),
        sa.Column("strike_price", sa.Float(), nullable=True),
        sa.Column("option_type", sa.String(5), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_index("ix_instruments_instrument_key", "instruments", ["instrument_key"])
    op.create_index("ix_instruments_symbol", "instruments", ["symbol"])


def downgrade() -> None:
    op.drop_index("ix_instruments_symbol", table_name="instruments")
    op.drop_index("ix_instruments_instrument_key", table_name="instruments")
    op.drop_table("instruments")
    op.drop_table("user_trading_configs")
