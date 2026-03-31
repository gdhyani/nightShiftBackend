import pandas as pd


class StoreCalculator:
    def calculate_sma(self, series: pd.Series, period: int = 20) -> pd.Series:
        return series.rolling(window=period).mean()

    def calculate_ema(self, series: pd.Series, period: int = 9) -> pd.Series:
        return series.ewm(span=period, adjust=False).mean()

    def calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        typical_price = (df["high"] + df["low"] + df["close"]) / 3
        cumulative_tp_vol = (typical_price * df["volume"]).cumsum()
        cumulative_vol = df["volume"].cumsum()
        return cumulative_tp_vol / cumulative_vol

    def calculate_all(self, df: pd.DataFrame) -> dict[str, float]:
        close = df["close"]
        results = {}

        sma_20 = self.calculate_sma(close, 20)
        results["sma_20"] = float(sma_20.iloc[-1]) if not pd.isna(sma_20.iloc[-1]) else None

        ema_9 = self.calculate_ema(close, 9)
        results["ema_9"] = float(ema_9.iloc[-1]) if not pd.isna(ema_9.iloc[-1]) else None

        rsi_14 = self.calculate_rsi(close, 14)
        results["rsi_14"] = float(rsi_14.iloc[-1]) if not pd.isna(rsi_14.iloc[-1]) else None

        vwap = self.calculate_vwap(df)
        results["vwap"] = float(vwap.iloc[-1]) if not pd.isna(vwap.iloc[-1]) else None

        return results
