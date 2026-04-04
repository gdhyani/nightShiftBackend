"""Indian market charge calculator for equity trades."""


class ChargeCalculator:
    """Calculates brokerage and regulatory charges for Indian equity trades."""

    def calculate(
        self,
        symbol: str,
        side: str,
        qty: float,
        price: float,
        product: str = "D",
        segment: str = "EQ",
    ) -> dict:
        """Calculate all charges for a trade.

        Args:
            symbol: Trading symbol.
            side: "BUY" or "SELL".
            qty: Quantity of shares.
            price: Price per share.
            product: "D" for delivery, "I" for intraday.
            segment: Market segment, default "EQ".

        Returns:
            Dict with brokerage, stt, exchange_charges, gst, stamp_duty,
            sebi_fee, total_charges, net_amount.
        """
        turnover = qty * price
        side_upper = side.upper()

        # Brokerage: flat ₹20 or 0.03%, whichever is lower
        brokerage = round(min(20.0, turnover * 0.0003), 2)

        # STT
        if product == "D":
            # Delivery: 0.1% both sides
            stt = round(turnover * 0.001, 2)
        else:
            # Intraday: 0.0125% sell-only
            stt = round(turnover * 0.000125, 2) if side_upper == "SELL" else 0.0

        # Exchange charges
        exchange_charges = round(turnover * 0.0000345, 2)

        # GST: 18% on (brokerage + exchange charges)
        gst = round((brokerage + exchange_charges) * 0.18, 2)

        # Stamp duty: buy-only
        stamp_duty = round(turnover * 0.00003, 2) if side_upper == "BUY" else 0.0

        # SEBI fee
        sebi_fee = round(turnover * 0.000001, 2)

        total_charges = round(
            brokerage + stt + exchange_charges + gst + stamp_duty + sebi_fee, 2
        )
        net_amount = round(turnover + total_charges, 2)

        return {
            "brokerage": brokerage,
            "stt": stt,
            "exchange_charges": exchange_charges,
            "gst": gst,
            "stamp_duty": stamp_duty,
            "sebi_fee": sebi_fee,
            "total_charges": total_charges,
            "net_amount": net_amount,
        }
