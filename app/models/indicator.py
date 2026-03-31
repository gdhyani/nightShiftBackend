from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Indicator(Base):
    __tablename__ = "indicators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        Index("ix_indicators_lookup", "symbol", "timeframe", "name", "timestamp", unique=True),
    )


class IndicatorSchema(BaseModel):
    id: int
    symbol: str
    timeframe: str
    timestamp: datetime
    name: str
    value: float

    model_config = {"from_attributes": True}
