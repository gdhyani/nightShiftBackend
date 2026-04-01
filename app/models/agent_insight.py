from datetime import datetime
from typing import Any

from pydantic import BaseModel
from sqlalchemy import DateTime, Float, Index, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AgentInsight(Base):
    __tablename__ = "agent_insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_name: Mapped[str] = mapped_column(String(50), nullable=False)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    timeframe: Mapped[str | None] = mapped_column(String(10), nullable=True)
    insight_type: Mapped[str] = mapped_column(String(50), nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("ix_agent_insights_lookup", "symbol", "expires_at"),
    )


class AgentInsightSchema(BaseModel):
    id: int
    agent_name: str
    symbol: str
    timeframe: str | None
    insight_type: str
    data: dict[str, Any]
    confidence: float | None
    created_at: datetime
    expires_at: datetime

    model_config = {"from_attributes": True}


class AgentInsightCreate(BaseModel):
    agent_name: str
    symbol: str
    timeframe: str | None = None
    insight_type: str
    data: dict[str, Any]
    confidence: float | None = None
    expires_at: datetime
