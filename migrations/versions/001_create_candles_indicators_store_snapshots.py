"""create candles indicators store_snapshots tables

Revision ID: 99d540a7b573
Revises:
Create Date: 2026-03-31
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "99d540a7b573"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "candles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("timeframe", sa.String(length=10), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Float(), nullable=False),
        sa.Column("high", sa.Float(), nullable=False),
        sa.Column("low", sa.Float(), nullable=False),
        sa.Column("close", sa.Float(), nullable=False),
        sa.Column("volume", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_candles_symbol_tf_ts",
        "candles",
        ["symbol", "timeframe", "timestamp"],
        unique=True,
    )

    # TimescaleDB hypertable (skip if TimescaleDB not installed)
    op.execute("""
        DO $$ BEGIN
            PERFORM create_hypertable('candles', 'timestamp', if_not_exists => TRUE);
        EXCEPTION WHEN undefined_function THEN
            RAISE NOTICE 'TimescaleDB not available, skipping hypertable creation';
        END $$;
    """)

    op.create_table(
        "indicators",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("timeframe", sa.String(length=10), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_indicators_lookup",
        "indicators",
        ["symbol", "timeframe", "name", "timestamp"],
        unique=True,
    )

    op.create_table(
        "store_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_store_snapshots_symbol", "store_snapshots", ["symbol"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_store_snapshots_symbol", table_name="store_snapshots")
    op.drop_table("store_snapshots")
    op.drop_index("ix_indicators_lookup", table_name="indicators")
    op.drop_table("indicators")
    op.drop_index("ix_candles_symbol_tf_ts", table_name="candles")
    op.drop_table("candles")
