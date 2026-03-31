import pandas as pd
import pytest

from app.services.store_calculator import StoreCalculator


@pytest.fixture
def calculator():
    return StoreCalculator()


@pytest.fixture
def sample_df():
    closes = [
        1.0800, 1.0840, 1.0860, 1.0880, 1.0835,
        1.0850, 1.0870, 1.0910, 1.0890, 1.0920,
        1.0900, 1.0880, 1.0860, 1.0840, 1.0870,
        1.0900, 1.0930, 1.0950, 1.0920, 1.0940,
    ]
    highs = [c + 0.005 for c in closes]
    lows = [c - 0.005 for c in closes]
    volumes = [1000 + i * 50 for i in range(20)]
    return pd.DataFrame(
        {
            "open": [c - 0.001 for c in closes],
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
        }
    )


def test_calculate_sma(calculator, sample_df):
    result = calculator.calculate_sma(sample_df["close"], period=5)
    assert len(result) == 20
    assert pd.isna(result.iloc[3])
    expected = sum([1.0800, 1.0840, 1.0860, 1.0880, 1.0835]) / 5
    assert abs(result.iloc[4] - expected) < 1e-6


def test_calculate_ema(calculator, sample_df):
    result = calculator.calculate_ema(sample_df["close"], period=5)
    assert len(result) == 20
    assert not pd.isna(result.iloc[5])
    assert isinstance(result.iloc[5], float)


def test_calculate_rsi(calculator, sample_df):
    result = calculator.calculate_rsi(sample_df["close"], period=14)
    assert len(result) == 20
    valid = result.dropna()
    assert all(0 <= v <= 100 for v in valid)


def test_calculate_vwap(calculator, sample_df):
    result = calculator.calculate_vwap(sample_df)
    assert len(result) == 20
    assert all(v > 0 for v in result)
    assert all(sample_df["low"].min() <= v <= sample_df["high"].max() for v in result)


def test_calculate_all_returns_dict(calculator, sample_df):
    result = calculator.calculate_all(sample_df)
    assert "sma_20" in result
    assert "ema_9" in result
    assert "rsi_14" in result
    assert "vwap" in result
    assert isinstance(result["rsi_14"], float)
