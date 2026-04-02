---
name: fair_value_gap
description: Detect and classify Fair Value Gaps in price action
---

# Fair Value Gap (FVG) Detection

## What is an FVG
A 3-candle pattern where the wick of candle 1 and wick of candle 3 do not overlap, leaving a gap in price.

## Detection Rules
- Bullish FVG: Candle 1 high < Candle 3 low (gap up)
- Bearish FVG: Candle 1 low > Candle 3 high (gap down)
- Minimum gap size: at least 1 ATR to be significant

## Classification
- Fresh: Price has not returned to the FVG zone
- Mitigated: Price has returned and partially filled the gap
- Filled: Price has completely closed the gap

## Entry Logic
- Wait for price to retrace INTO the FVG zone
- Confirm with a rejection wick or volume spike at the zone
- Optimal trade entry (OTE) at 50% of FVG zone
- Stop loss beyond the full FVG range

## Confluence Checks
- FVG inside an order block increases confidence
- FVG aligned with premium/discount zone adds directional bias
- Multiple timeframe FVG alignment is the strongest signal
