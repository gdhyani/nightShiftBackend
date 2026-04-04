"""Tests for the paper trading engine."""

import pytest
from sqlalchemy import select

from app.models.trade import Position, Trade
from app.services.paper_engine import PaperEngine


class TestPaperEngine:
    @pytest.fixture
    def engine(self):
        return PaperEngine()

    async def test_place_market_order(self, db_session, engine):
        """Market order should be filled with charges and create Trade + Position."""
        result = await engine.place_order(
            session=db_session,
            symbol="RELIANCE",
            side="BUY",
            qty=10,
            order_type="MARKET",
            price=2500.0,
        )

        assert result["status"] == "filled"
        assert result["order_id"] is not None
        assert result["charges"]["total_charges"] > 0
        assert result["source"] == "paper"

        # Verify Trade record
        trade = await db_session.get(Trade, result["order_id"])
        assert trade is not None
        assert trade.source == "paper"
        assert trade.status == "open"

        # Verify Position record
        stmt = select(Position).where(Position.trade_id == trade.id)
        pos_result = await db_session.execute(stmt)
        position = pos_result.scalar_one()
        assert position is not None
        assert position.status == "open"

    async def test_close_paper_trade(self, db_session, engine):
        """Close a BUY trade at higher price, pnl should be positive."""
        order = await engine.place_order(
            session=db_session,
            symbol="TCS",
            side="BUY",
            qty=10,
            order_type="MARKET",
            price=2500.0,
        )

        close_result = await engine.close_trade(
            session=db_session,
            trade_id=order["order_id"],
            exit_price=2550.0,
        )

        assert close_result["status"] == "closed"
        assert close_result["pnl"] > 0

    async def test_slippage_applied(self, db_session):
        """With 0.1% slippage, BUY fill should be higher than requested price."""
        engine = PaperEngine(slippage_pct=0.001)
        result = await engine.place_order(
            session=db_session,
            symbol="INFY",
            side="BUY",
            qty=10,
            order_type="MARKET",
            price=2500.0,
        )

        assert result["fill_price"] > 2500.0
        assert result["fill_price"] < 2510.0
