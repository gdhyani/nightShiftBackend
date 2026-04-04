"""Tests for the Indian market charge calculator."""

from app.services.charge_calculator import ChargeCalculator


class TestChargeCalculator:
    def setup_method(self):
        self.calc = ChargeCalculator()

    def test_delivery_buy_charges(self):
        """Delivery buy: brokerage capped at 20, STT > 0, stamp_duty > 0."""
        # turnover = 250000, brokerage = min(20, 75) = 20
        result = self.calc.calculate("RELIANCE", "BUY", 100, 2500.0, product="D")
        assert result["brokerage"] == 20.0
        assert result["stt"] > 0
        assert result["stamp_duty"] > 0

    def test_delivery_sell_charges(self):
        """Delivery sell: stamp_duty should be 0."""
        result = self.calc.calculate("RELIANCE", "SELL", 100, 2500.0, product="D")
        assert result["stamp_duty"] == 0.0
        assert result["stt"] > 0

    def test_intraday_sell_stt(self):
        """Intraday sell: STT should be > 0."""
        result = self.calc.calculate("RELIANCE", "SELL", 100, 2500.0, product="I")
        assert result["stt"] > 0

    def test_intraday_buy_no_stt(self):
        """Intraday buy: STT should be 0."""
        result = self.calc.calculate("RELIANCE", "BUY", 100, 2500.0, product="I")
        assert result["stt"] == 0.0

    def test_charges_return_all_fields(self):
        """All 8 expected keys must be present."""
        result = self.calc.calculate("TCS", "BUY", 50, 3500.0)
        expected_keys = {
            "brokerage",
            "stt",
            "exchange_charges",
            "gst",
            "stamp_duty",
            "sebi_fee",
            "total_charges",
            "net_amount",
        }
        assert set(result.keys()) == expected_keys
