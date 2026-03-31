from datetime import datetime
from typing import Any

from pydantic import BaseModel
from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StoreSnapshot(Base):
    __tablename__ = "store_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )


class StoreSnapshotSchema(BaseModel):
    symbol: str
    data: dict[str, Any]
    updated_at: datetime

    model_config = {"from_attributes": True}
