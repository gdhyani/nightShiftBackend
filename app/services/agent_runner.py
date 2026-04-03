import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.tier1 import correlation_agent, news_agent, order_flow_agent, session_agent
from app.agents.tier2 import bias_agent, liquidity_agent, range_agent, structure_agent
from app.core.config import settings
from app.models import AgentInsight

logger = logging.getLogger(__name__)

AGENT_REGISTRY = {
    "news_agent": {"module": news_agent, "interval_attr": "agent_news_interval"},
    "order_flow_agent": {"module": order_flow_agent, "interval_attr": "agent_order_flow_interval"},
    "session_agent": {"module": session_agent, "interval_attr": "agent_session_interval"},
    "correlation_agent": {
        "module": correlation_agent,
        "interval_attr": "agent_correlation_interval",
    },
    "range_agent": {"module": range_agent, "interval_attr": "agent_range_interval"},
    "bias_agent": {"module": bias_agent, "interval_attr": "agent_bias_interval"},
    "liquidity_agent": {"module": liquidity_agent, "interval_attr": "agent_liquidity_interval"},
    "structure_agent": {"module": structure_agent, "interval_attr": "agent_structure_interval"},
}


class AgentRunner:
    def __init__(self, session_factory, ws_manager=None):
        self._session_factory = session_factory
        self._ws_manager = ws_manager
        self._tasks: list[asyncio.Task] = []

    async def save_insight(self, session: AsyncSession, agent_name: str, symbol: str,
                          insight_type: str, data: dict, confidence: float | None = None,
                          ttl_minutes: int = 60) -> None:
        now = datetime.now(timezone.utc)
        insight = AgentInsight(
            agent_name=agent_name,
            symbol=symbol,
            insight_type=insight_type,
            data=data,
            confidence=confidence,
            created_at=now,
            expires_at=now + timedelta(minutes=ttl_minutes),
        )
        session.add(insight)
        await session.commit()

    async def run_agent_loop(self, agent_name: str, module, interval: int) -> None:
        logger.info(f"Starting {agent_name} loop (interval: {interval}s)")
        while True:
            for symbol in settings.watchlist_symbols:
                try:
                    async with self._session_factory() as session:
                        result = await module.run(session, symbol)
                        ttl = result.pop("_ttl_minutes", 60)
                        confidence = result.get("confidence")
                        await self.save_insight(
                            session=session,
                            agent_name=agent_name,
                            symbol=symbol,
                            insight_type=module.INSIGHT_TYPE,
                            data=result,
                            confidence=confidence,
                            ttl_minutes=ttl,
                        )
                    if self._ws_manager:
                        await self._ws_manager.broadcast("agent_update", {
                            "channel": "agent_update",
                            "agent_name": agent_name,
                            "symbol": symbol,
                            "insight_type": module.INSIGHT_TYPE,
                        })
                    logger.info(f"{agent_name} completed for {symbol}")
                except Exception as e:
                    logger.error(f"{agent_name} failed for {symbol}: {e}")
            await asyncio.sleep(interval)

    def start_all(self) -> None:
        for name, config in AGENT_REGISTRY.items():
            interval = getattr(settings, config["interval_attr"])
            task = asyncio.create_task(self.run_agent_loop(name, config["module"], interval))
            self._tasks.append(task)
        logger.info(f"Started {len(self._tasks)} agent loops")

    def stop_all(self) -> None:
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()

    @staticmethod
    def list_agents() -> list[dict]:
        agents = []
        for name, config in AGENT_REGISTRY.items():
            module = config["module"]
            interval = getattr(settings, config["interval_attr"])
            agents.append({
                "name": name,
                "insight_type": module.INSIGHT_TYPE,
                "interval_seconds": interval,
                "tier": 1 if "tier1" in module.__name__ else 2,
            })
        return agents
