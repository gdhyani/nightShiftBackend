from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import DailyReport, DailyReportSchema

router = APIRouter(tags=["reports"])


@router.get("/api/reports", response_model=list[DailyReportSchema])
async def list_reports(
    limit: int = 30,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(DailyReport).order_by(DailyReport.date.desc()).limit(limit)
    )
    return result.scalars().all()


@router.get("/api/reports/{date}", response_model=DailyReportSchema)
async def get_report(date: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(DailyReport).where(DailyReport.date == date)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
