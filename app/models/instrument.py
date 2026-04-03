from datetime import date, datetime

from pydantic import BaseModel
from sqlalchemy import Date, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _utcnow():
    from datetime import timezone
    return datetime.now(timezone.utc)


class Instrument(Base):
    __tablename__ = "instruments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instrument_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), default="")
    exchange: Mapped[str] = mapped_column(String(10), default="")
    segment: Mapped[str] = mapped_column(String(10), default="")
    isin: Mapped[str | None] = mapped_column(String(20), nullable=True)
    lot_size: Mapped[int] = mapped_column(Integer, default=1)
    tick_size: Mapped[float] = mapped_column(Float, default=0.05)
    instrument_type: Mapped[str | None] = mapped_column(String(10), nullable=True)
    expiry: Mapped[date | None] = mapped_column(Date, nullable=True)
    strike_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    option_type: Mapped[str | None] = mapped_column(String(5), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class InstrumentSchema(BaseModel):
    id: int
    instrument_key: str
    symbol: str
    name: str
    exchange: str
    segment: str
    isin: str | None
    lot_size: int
    tick_size: float
    instrument_type: str | None
    expiry: date | None
    strike_price: float | None
    option_type: str | None
    updated_at: datetime
    model_config = {"from_attributes": True}
