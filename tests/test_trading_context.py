from unittest.mock import AsyncMock
import pytest
from app.services.charge_calculator import ChargeCalculator
from app.services.paper_engine import PaperEngine
from app.services.trading_context import TradingContext


async def test_paper_mode_uses_paper_engine(db_session):
    mock_tm = AsyncMock()
    mock_tm.get_read_token = AsyncMock(return_value="tok")
    mock_upstox = AsyncMock()
    mock_upstox.get_ltp = AsyncMock(
        return_value={"NSE_EQ|INE848E01016": {"last_price": 2500.0}}
    )
    ctx = TradingContext(
        session=db_session, token_manager=mock_tm, upstox=mock_upstox,
        paper_engine=PaperEngine(slippage_pct=0), charge_calc=ChargeCalculator(),
        mode="paper",
    )
    assert ctx.get_mode() == "paper"
    result = await ctx.place_order(
        symbol="NSE_EQ|INE848E01016", side="BUY", qty=10,
        order_type="MARKET", price=2500.0,
    )
    assert result["status"] == "filled"
    assert result["source"] == "paper"


async def test_calculate_charges(db_session):
    ctx = TradingContext(
        session=db_session, token_manager=AsyncMock(), upstox=AsyncMock(),
        paper_engine=PaperEngine(), charge_calc=ChargeCalculator(), mode="paper",
    )
    charges = await ctx.calculate_charges("X", "BUY", 10, 2500.0)
    assert "total_charges" in charges
    assert charges["total_charges"] > 0


async def test_get_positions(db_session):
    ctx = TradingContext(
        session=db_session, token_manager=AsyncMock(), upstox=AsyncMock(),
        paper_engine=PaperEngine(), charge_calc=ChargeCalculator(), mode="paper",
    )
    positions = await ctx.get_positions()
    assert isinstance(positions, list)
