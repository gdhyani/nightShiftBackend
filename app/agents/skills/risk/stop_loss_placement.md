---
name: stop_loss_placement
description: Rules for optimal stop loss placement to protect capital
---

# Stop Loss Placement

## Rules
- Place stop loss beyond the invalidation point of your setup
- For order block entries: stop below/above the OB body + 1 ATR buffer
- For FVG entries: stop beyond the full FVG range
- For liquidity sweep entries: stop beyond the sweep high/low

## Buffer Guidelines
- Add 1 ATR buffer beyond the technical level
- Never place stop at an obvious level (equal highs/lows = liquidity target)
- Account for spread in forex/volatile instruments

## Position Sizing Integration
- Calculate position size AFTER determining stop distance
- Risk = entry_price - stop_loss (or stop_loss - entry_price for shorts)
- Position size = (account_risk_amount) / risk_per_unit
- Never risk more than 1-2% of account on a single trade

## Trailing Stop Rules
- Move stop to breakeven after price reaches 1R profit
- Trail stop behind swing points in the direction of the trade
- Never widen a stop loss — only tighten
