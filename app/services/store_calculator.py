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

    def calculate_macd(
        self, series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> dict[str, pd.Series]:
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return {"macd_line": macd_line, "signal_line": signal_line, "histogram": histogram}

    def calculate_bollinger_bands(
        self, series: pd.Series, period: int = 20, std_dev: float = 2.0
    ) -> dict[str, pd.Series]:
        middle = series.rolling(window=period).mean()
        rolling_std = series.rolling(window=period).std()
        upper = middle + std_dev * rolling_std
        lower = middle - std_dev * rolling_std
        return {"upper": upper, "middle": middle, "lower": lower}

    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        high_low = df["high"] - df["low"]
        high_prev_close = (df["high"] - df["close"].shift(1)).abs()
        low_prev_close = (df["low"] - df["close"].shift(1)).abs()
        true_range = pd.concat([high_low, high_prev_close, low_prev_close], axis=1).max(axis=1)
        return true_range.ewm(com=period - 1, min_periods=period).mean()

    def _latest(self, series: pd.Series) -> float | None:
        val = series.iloc[-1]
        return float(val) if not pd.isna(val) else None

    def calculate_all(self, df: pd.DataFrame) -> dict[str, float | None]:
        close = df["close"]
        results = {}

        for period in [20, 50]:
            results[f"sma_{period}"] = self._latest(self.calculate_sma(close, period))

        for period in [9, 20, 50]:
            results[f"ema_{period}"] = self._latest(self.calculate_ema(close, period))

        results["rsi_14"] = self._latest(self.calculate_rsi(close, 14))
        results["vwap"] = self._latest(self.calculate_vwap(df))

        macd = self.calculate_macd(close)
        results["macd_line"] = self._latest(macd["macd_line"])
        results["macd_signal"] = self._latest(macd["signal_line"])
        results["macd_histogram"] = self._latest(macd["histogram"])

        bb = self.calculate_bollinger_bands(close)
        results["bb_upper"] = self._latest(bb["upper"])
        results["bb_middle"] = self._latest(bb["middle"])
        results["bb_lower"] = self._latest(bb["lower"])

        results["atr_14"] = self._latest(self.calculate_atr(df, 14))

        return results
