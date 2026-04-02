import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.tier3 import analyst_agent, evaluator_agent
from app.models import Strategy, StrategyRun
from app.services.trade_executor import MockExecutor

logger = logging.getLogger(__name__)


class StrategyRunner:
    def __init__(self, session_factory, ws_manager=None):
        self._session_factory = session_factory
        self._ws_manager = ws_manager
        self._executor = MockExecutor()
        self._tasks: list[asyncio.Task] = []

    async def run_pipeline(self, session: AsyncSession, strategy: Strategy, symbol: str) -> dict:
        stages = []

        logger.info(f"[{strategy.name}] Running analyst for {symbol}")
        analysis = await analyst_agent.run(session, symbol)
        stages.append({"agent": "analyst", "output": analysis})

        logger.info(f"[{strategy.name}] Running evaluator for {symbol}")
        evaluation = await evaluator_agent.run(session, symbol, analysis)
        stages.append({"agent": "evaluator", "output": evaluation})

        decision = evaluation.get("decision", "SKIP")
        trade_id = None

        if decision == "EXECUTE":
            direction = evaluation.get("direction")
            entry = evaluation.get("entry_price")
            sl = evaluation.get("stop_loss")
            tp = evaluation.get("take_profit")
            qty = evaluation.get("quantity", 0.1)

            if direction and entry and sl and tp:
                trade = await self._executor.open_trade(
                    session=session, strategy_id=strategy.id, symbol=symbol,
                    direction=direction, entry_price=entry, stop_loss=sl,
                    take_profit=tp, quantity=qty,
                    reasoning={"analysis": analysis, "evaluation": evaluation},
                )
                trade_id = trade.id
                logger.info(f"[{strategy.name}] Trade opened: {direction} {symbol} @ {entry}")
            else:
                logger.warning(f"[{strategy.name}] EXECUTE but missing trade params")
                decision = "SKIP"

        run = StrategyRun(
            strategy_id=strategy.id, symbol=symbol,
            stages={"stages": stages}, decision=decision, trade_id=trade_id,
        )
        session.add(run)
        await session.commit()
        return {"decision": decision, "trade_id": trade_id}

    async def run_strategy_loop(self, strategy_id: int) -> None:
        while True:
            try:
                async with self._session_factory() as session:
                    result = await session.execute(
                        select(Strategy).where(Strategy.id == strategy_id)
                    )
                    strategy = result.scalar_one_or_none()
                    if not strategy or not strategy.enabled:
                        await asyncio.sleep(30)
                        continue

                    for symbol in strategy.symbols_list:
                        try:
                            async with self._session_factory() as run_session:
                                result = await self.run_pipeline(run_session, strategy, symbol)
                            if self._ws_manager:
                                await self._ws_manager.broadcast("strategy_update", {
                                    "channel": "strategy_update",
                                    "strategy_id": strategy_id,
                                    "symbol": symbol,
                                    "decision": result["decision"],
                                })
                        except Exception as e:
                            logger.error(f"Pipeline failed for {strategy.name}/{symbol}: {e}")
                    await asyncio.sleep(strategy.schedule_interval)
            except Exception as e:
                logger.error(f"Strategy loop error for id={strategy_id}: {e}")
                await asyncio.sleep(60)

    async def start_strategies(self) -> None:
        async with self._session_factory() as session:
            result = await session.execute(select(Strategy).where(Strategy.enabled == True))
            strategies = result.scalars().all()
        for strategy in strategies:
            task = asyncio.create_task(self.run_strategy_loop(strategy.id))
            self._tasks.append(task)
            logger.info(f"Started strategy loop: {strategy.name} (id={strategy.id})")

    def stop_all(self) -> None:
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()
