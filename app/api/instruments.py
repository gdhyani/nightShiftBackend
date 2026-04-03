from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import InstrumentSchema
from app.services.instrument_service import InstrumentService

router = APIRouter(prefix="/api/instruments", tags=["instruments"])

_svc = InstrumentService()


@router.get("/search", response_model=list[InstrumentSchema])
async def search_instruments(
    q: str = Query(..., min_length=1),
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    return await _svc.search(session, q, limit)


@router.get("/{instrument_key:path}", response_model=InstrumentSchema)
async def get_instrument(
    instrument_key: str,
    session: AsyncSession = Depends(get_session),
):
    inst = await _svc.get_by_key(session, instrument_key)
    if inst is None:
        raise HTTPException(404, "Instrument not found")
    return inst
