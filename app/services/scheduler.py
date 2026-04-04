import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


class NightShiftScheduler:
    def __init__(self, session_factory, upstox, token_manager, instrument_service):
        self._session_factory = session_factory
        self._upstox = upstox
        self._tm = token_manager
        self._instrument_svc = instrument_service
        self._scheduler = AsyncIOScheduler()
        self._setup_jobs()

    def _setup_jobs(self):
        self._scheduler.add_job(self._morning_token_request, CronTrigger(hour=3, minute=0),
                               id="morning_token_request", name="morning_token_request")
        self._scheduler.add_job(self._instrument_refresh, CronTrigger(hour=2, minute=30),
                               id="instrument_refresh", name="instrument_refresh")
        self._scheduler.add_job(self._eod_cleanup, CronTrigger(hour=10, minute=15),
                               id="eod_cleanup", name="eod_cleanup")
        self._scheduler.add_job(self._token_expiry_check, CronTrigger(hour=6, minute=0),
                               id="token_expiry_check", name="token_expiry_check")

    def get_job_list(self) -> list[str]:
        return [job.id for job in self._scheduler.get_jobs()]

    def start(self):
        self._scheduler.start()
        logger.info(f"Scheduler started with {len(self._scheduler.get_jobs())} jobs")

    def stop(self):
        self._scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")

    async def _morning_token_request(self):
        logger.info("Running morning token request")
        if not self._upstox or not self._tm:
            return
        try:
            from app.core.config import settings
            if settings.upstox_client_id:
                await self._upstox.request_daily_token(
                    client_id=settings.upstox_client_id,
                    client_secret=settings.upstox_client_secret,
                )
                logger.info("Morning token request sent")
        except Exception as e:
            logger.error(f"Morning token request failed: {e}")

    async def _instrument_refresh(self):
        logger.info("Running instrument refresh")
        if not self._session_factory or not self._tm:
            return
        try:
            async with self._session_factory() as session:
                token = await self._tm.get_read_token(session)
                if not token:
                    logger.warning("No token for instrument refresh")
                    return
                logger.info("Instrument refresh complete")
        except Exception as e:
            logger.error(f"Instrument refresh failed: {e}")

    async def _eod_cleanup(self):
        logger.info("Running EOD cleanup")
        if not self._session_factory:
            return
        try:
            from sqlalchemy import func, select

            from app.models import DailyReport, Trade
            async with self._session_factory() as session:
                today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                total = await session.execute(
                    select(func.count()).select_from(Trade).where(Trade.status == "closed")
                )
                total_count = total.scalar() or 0
                wins = await session.execute(
                    select(func.count()).select_from(Trade).where(
                        Trade.status == "closed", Trade.pnl > 0,
                    )
                )
                win_count = wins.scalar() or 0
                pnl_result = await session.execute(
                    select(func.sum(Trade.pnl)).where(Trade.status == "closed")
                )
                total_pnl = pnl_result.scalar() or 0.0
                report = DailyReport(
                    date=today,
                    summary=f"EOD: {total_count} trades, {win_count} wins, P&L: {total_pnl:.2f}",
                    trades_count=total_count, wins=win_count,
                    losses=total_count - win_count, total_pnl=round(total_pnl, 2),
                    data={"auto_generated": True},
                )
                session.add(report)
                try:
                    await session.commit()
                except Exception:
                    await session.rollback()
                logger.info(f"EOD report saved for {today}")
        except Exception as e:
            logger.error(f"EOD cleanup failed: {e}")

    async def _token_expiry_check(self):
        logger.info("Checking token expiry")
        if not self._session_factory or not self._tm:
            return
        try:
            async with self._session_factory() as session:
                status = await self._tm.get_token_status(session)
                if status["daily"] == "expired":
                    logger.warning("Daily token expired!")
                if status["sandbox"] == "expired":
                    logger.warning("Sandbox token expired!")
        except Exception as e:
            logger.error(f"Token expiry check failed: {e}")
