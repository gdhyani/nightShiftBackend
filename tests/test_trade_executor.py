from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.models import Trade, Position
from app.services.trade_executor import MockExecutor


async def test_open_trade(db_session):
    executor = MockExecutor()
    trade = await executor.open_trade(
        session=db_session,
        strategy_id=1,
        symbol="EUR_USD",
        direction="BUY",
        entry_price=1.0850,
        stop_loss=1.0820,
        take_profit=1.0920,
        quantity=0.1,
        reasoning={"decision": "EXECUTE", "confidence": 0.8},
    )
    assert trade.id is not None
    assert trade.status == "open"
    assert trade.entry_price == 1.0850

    result = await db_session.execute(
        select(Position).where(Position.trade_id == trade.id)
    )
    position = result.scalar_one()
    assert position.symbol == "EUR_USD"
    assert position.status == "open"


async def test_close_trade(db_session):
    executor = MockExecutor()
    trade = await executor.open_trade(
        session=db_session,
        strategy_id=1,
        symbol="EUR_USD",
        direction="BUY",
        entry_price=1.0850,
        stop_loss=1.0820,
        take_profit=1.0920,
        quantity=0.1,
        reasoning={},
    )
    closed = await executor.close_trade(
        session=db_session, trade_id=trade.id, exit_price=1.0900
    )
    assert closed.status == "closed"
    assert closed.exit_price == 1.0900
    assert closed.pnl == pytest.approx((1.0900 - 1.0850) * 0.1, abs=1e-6)

    result = await db_session.execute(
        select(Position).where(Position.trade_id == trade.id)
    )
    position = result.scalar_one()
    assert position.status == "closed"


async def test_close_sell_trade_pnl(db_session):
    executor = MockExecutor()
    trade = await executor.open_trade(
        session=db_session,
        strategy_id=1,
        symbol="EUR_USD",
        direction="SELL",
        entry_price=1.0900,
        stop_loss=1.0930,
        take_profit=1.0850,
        quantity=0.1,
        reasoning={},
    )
    closed = await executor.close_trade(
        session=db_session, trade_id=trade.id, exit_price=1.0850
    )
    assert closed.pnl == pytest.approx((1.0900 - 1.0850) * 0.1, abs=1e-6)
