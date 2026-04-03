from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _utcnow():
    from datetime import timezone
    return datetime.now(timezone.utc)


class UserTradingConfig(Base):
    __tablename__ = "user_trading_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(50), unique=True, default="default")
    upstox_client_id: Mapped[str] = mapped_column(String(100), default="")
    upstox_client_secret_enc: Mapped[str] = mapped_column(Text, default="")
    daily_token_enc: Mapped[str] = mapped_column(Text, default="")
    daily_token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sandbox_token_enc: Mapped[str] = mapped_column(Text, default="")
    sandbox_token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    default_mode: Mapped[str] = mapped_column(String(10), default="paper")
    notifier_url: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class UserTradingConfigSchema(BaseModel):
    id: int
    user_id: str
    upstox_client_id: str
    default_mode: str
    daily_token_status: str
    sandbox_token_status: str
    notifier_url: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
