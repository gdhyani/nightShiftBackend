import pandas as pd
import pytest
import numpy as np

from app.services.store_calculator import StoreCalculator


@pytest.fixture
def calculator():
    return StoreCalculator()


@pytest.fixture
def large_df():
    np.random.seed(42)
    base_price = 1.0800
    closes = [base_price]
    for _ in range(49):
        closes.append(closes[-1] + np.random.normal(0, 0.002))
    closes = [round(c, 5) for c in closes]
    highs = [c + abs(np.random.normal(0, 0.001)) for c in closes]
    lows = [c - abs(np.random.normal(0, 0.001)) for c in closes]
    volumes = [1000 + i * 20 for i in range(50)]
    return pd.DataFrame({
        "open": [c - 0.0005 for c in closes],
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


def test_calculate_macd(calculator, large_df):
    result = calculator.calculate_macd(large_df["close"])
    assert "macd_line" in result
    assert "signal_line" in result
    assert "histogram" in result
    assert len(result["macd_line"]) == 50
    assert not pd.isna(result["macd_line"].iloc[-1])
    assert not pd.isna(result["signal_line"].iloc[-1])


def test_calculate_bollinger_bands(calculator, large_df):
    result = calculator.calculate_bollinger_bands(large_df["close"])
    assert "upper" in result
    assert "middle" in result
    assert "lower" in result
    valid_idx = result["upper"].dropna().index
    for i in valid_idx:
        assert result["upper"].iloc[i] >= result["middle"].iloc[i]
        assert result["middle"].iloc[i] >= result["lower"].iloc[i]


def test_calculate_atr(calculator, large_df):
    result = calculator.calculate_atr(large_df)
    assert len(result) == 50
    valid = result.dropna()
    assert len(valid) > 0
    assert all(v > 0 for v in valid)


def test_calculate_all_has_expanded_keys(calculator, large_df):
    result = calculator.calculate_all(large_df)
    expected_keys = [
        "sma_20", "sma_50", "ema_9", "ema_20", "ema_50",
        "rsi_14", "vwap",
        "macd_line", "macd_signal", "macd_histogram",
        "bb_upper", "bb_middle", "bb_lower",
        "atr_14",
    ]
    for key in expected_keys:
        assert key in result, f"Missing key: {key}"
