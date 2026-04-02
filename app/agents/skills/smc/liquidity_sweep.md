---
name: liquidity_sweep
description: Identify liquidity pools and detect sweeps
---

# Liquidity Sweep Detection

## Liquidity Pools
- Buy-side liquidity: Clusters of stops above swing highs, equal highs
- Sell-side liquidity: Clusters below swing lows, equal lows
- Price is drawn to liquidity before reversals

## Equal Highs / Equal Lows
- Two or more swing highs at approximately the same level = resting buy-side liquidity
- Two or more swing lows at approximately the same level = resting sell-side liquidity

## Sweep Detection
- A sweep occurs when price takes out a liquidity level then reverses
- Look for: wick above/below the level followed by close back inside range
- Sweep + displacement = high-probability reversal signal

## Trading Rules
- After buy-side liquidity is swept: look for short entries
- After sell-side liquidity is swept: look for long entries
- Combine with OB/FVG for entry refinement
