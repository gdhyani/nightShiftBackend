from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import StoreSnapshot, StoreSnapshotSchema

router = APIRouter(prefix="/api/store", tags=["store"])


@router.get("/{symbol}", response_model=StoreSnapshotSchema)
async def get_store_snapshot(
    symbol: str,
    session: AsyncSession = Depends(get_session),
):
    query = select(StoreSnapshot).where(StoreSnapshot.symbol == symbol)
    result = await session.execute(query)
    snapshot = result.scalar_one_or_none()
    if snapshot is None:
        raise HTTPException(status_code=404, detail=f"No store snapshot for {symbol}")
    return snapshot
