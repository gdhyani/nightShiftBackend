"""create agent_insights table

Revision ID: a1b2c3d4e5f6
Revises: 99d540a7b573
Create Date: 2026-04-01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "99d540a7b573"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agent_insights",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("agent_name", sa.String(length=50), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("timeframe", sa.String(length=10), nullable=True),
        sa.Column("insight_type", sa.String(length=50), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_insights_lookup", "agent_insights", ["symbol", "expires_at"])


def downgrade() -> None:
    op.drop_index("ix_agent_insights_lookup", table_name="agent_insights")
    op.drop_table("agent_insights")
