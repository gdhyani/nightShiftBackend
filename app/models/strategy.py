from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Strategy(Base):
    __tablename__ = "strategies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    symbols: Mapped[str] = mapped_column(String(500), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    schedule_interval: Mapped[int] = mapped_column(Integer, nullable=False, default=1800)
    event_triggers: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pipeline_config: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    @property
    def symbols_list(self) -> list[str]:
        return [s.strip() for s in self.symbols.split(",") if s.strip()]


class StrategySchema(BaseModel):
    id: int
    name: str
    symbols: str
    enabled: bool
    schedule_interval: int
    event_triggers: str | None
    pipeline_config: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StrategyCreate(BaseModel):
    name: str
    symbols: str
    enabled: bool = True
    schedule_interval: int = 1800
    event_triggers: str | None = None
    pipeline_config: dict[str, Any]


class StrategyUpdate(BaseModel):
    name: str | None = None
    symbols: str | None = None
    enabled: bool | None = None
    schedule_interval: int | None = None
    event_triggers: str | None = None
    pipeline_config: dict[str, Any] | None = None


class StrategyRun(Base):
    __tablename__ = "strategy_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    strategy_id: Mapped[int] = mapped_column(Integer, nullable=False)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    stages: Mapped[dict] = mapped_column(JSON, nullable=False)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    trade_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )


class StrategyRunSchema(BaseModel):
    id: int
    strategy_id: int
    symbol: str
    stages: dict[str, Any]
    decision: str
    trade_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
