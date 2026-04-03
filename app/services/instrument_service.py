import logging

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.instrument import Instrument

logger = logging.getLogger(__name__)


class InstrumentService:
    async def search(
        self, session: AsyncSession, query: str, limit: int = 20
    ) -> list[Instrument]:
        result = await session.execute(
            select(Instrument)
            .where(
                or_(
                    Instrument.symbol.ilike(f"%{query}%"),
                    Instrument.name.ilike(f"%{query}%"),
                )
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_key(
        self, session: AsyncSession, instrument_key: str
    ) -> Instrument | None:
        result = await session.execute(
            select(Instrument).where(Instrument.instrument_key == instrument_key)
        )
        return result.scalar_one_or_none()

    async def sync_from_list(
        self, session: AsyncSession, instruments: list[dict]
    ) -> int:
        new_count = 0
        for data in instruments:
            existing = await session.execute(
                select(Instrument).where(
                    Instrument.instrument_key == data["instrument_key"]
                )
            )
            inst = existing.scalar_one_or_none()
            if inst is not None:
                for key, value in data.items():
                    if key != "instrument_key":
                        setattr(inst, key, value)
            else:
                session.add(Instrument(**data))
                new_count += 1
        await session.commit()
        return new_count
