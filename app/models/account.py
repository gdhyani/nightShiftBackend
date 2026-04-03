from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel
from sqlalchemy import JSON, DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    balance: Mapped[float] = mapped_column(Float, nullable=False, default=10000.0)
    equity: Mapped[float] = mapped_column(Float, nullable=False, default=10000.0)
    margin_used: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    daily_loss_limit: Mapped[float] = mapped_column(Float, nullable=False, default=500.0)
    max_drawdown: Mapped[float] = mapped_column(Float, nullable=False, default=2000.0)
    max_position_size: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    risk_per_trade: Mapped[float] = mapped_column(Float, nullable=False, default=0.02)
    settings: Mapped[dict | None] = mapped_column(JSON, nullable=False, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )


class AccountSchema(BaseModel):
    id: int
    balance: float
    equity: float
    margin_used: float
    daily_loss_limit: float
    max_drawdown: float
    max_position_size: float
    risk_per_trade: float
    settings: dict[str, Any] | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class AccountUpdate(BaseModel):
    balance: float | None = None
    equity: float | None = None
    margin_used: float | None = None
    daily_loss_limit: float | None = None
    max_drawdown: float | None = None
    max_position_size: float | None = None
    risk_per_trade: float | None = None
    settings: dict[str, Any] | None = None
