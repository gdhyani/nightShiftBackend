import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.agents.tier4 import chat_reporter, performance_tracker, trade_reviewer
from app.models import DailyReport

logger = logging.getLogger(__name__)


class ReviewRunner:
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def run_daily_review(self) -> DailyReport:
        """Run performance_tracker, trade_reviewer, chat_reporter in sequence.
        Saves and returns a DailyReport."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        logger.info(f"Starting daily review for {today}")

        # Step 1: Performance tracking (pure computation)
        async with self.session_factory() as session:
            performance = await performance_tracker.run(session)
        logger.info(f"Performance: {performance}")

        # Step 2: Trade review (LLM-based)
        async with self.session_factory() as session:
            review = await trade_reviewer.run(session)
        logger.info(f"Trade review complete: {len(review.get('reviews', []))} trades reviewed")

        # Step 3: Chat report (LLM-based)
        report_data = await chat_reporter.run(performance, review)
        logger.info(f"Chat report generated")

        # Save daily report to DB
        async with self.session_factory() as session:
            report = DailyReport(
                date=today,
                summary=report_data.get("summary", "No summary generated."),
                trades_count=performance.get("total_trades", 0),
                wins=performance.get("wins", 0),
                losses=performance.get("losses", 0),
                total_pnl=performance.get("total_pnl", 0.0),
                data={
                    "performance": performance,
                    "review": review,
                    "report": report_data,
                },
            )
            session.add(report)
            await session.commit()
            await session.refresh(report)
            logger.info(f"Daily report saved: {report.id}")
            return report
