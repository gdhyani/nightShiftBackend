---
name: retest_confirmation
description: Rules for confirming entries via retests
---

# Retest Confirmation

## Rules
- After identifying a setup (OB, FVG, breaker), do NOT enter immediately
- Wait for price to retrace/retest the zone
- Minimum 2 rejection candles at the zone
- Volume should increase on the rejection candles
- The retest candle body should close outside the zone

## Invalid Retests
- Price closes through the zone = zone invalidated
- No rejection wick = weak retest, skip
- Decreasing volume on retest = lack of interest, skip
