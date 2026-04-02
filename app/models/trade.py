from datetime import datetime
from typing import Any

from pydantic import BaseModel
from sqlalchemy import DateTime, Float, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    strategy_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    exit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    take_profit: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    pnl: Mapped[float | None] = mapped_column(Float, nullable=True)
    reasoning: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )


class TradeSchema(BaseModel):
    id: int
    strategy_id: int | None
    symbol: str
    direction: str
    entry_price: float
    exit_price: float | None
    stop_loss: float
    take_profit: float
    quantity: float
    status: str
    pnl: float | None
    reasoning: dict[str, Any] | None
    opened_at: datetime | None
    closed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trade_id: Mapped[int] = mapped_column(Integer, nullable=False)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    take_profit: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unrealized_pnl: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PositionSchema(BaseModel):
    id: int
    trade_id: int
    symbol: str
    direction: str
    entry_price: float
    current_price: float
    stop_loss: float
    take_profit: float
    quantity: float
    unrealized_pnl: float
    status: str
    opened_at: datetime | None

    model_config = {"from_attributes": True}
