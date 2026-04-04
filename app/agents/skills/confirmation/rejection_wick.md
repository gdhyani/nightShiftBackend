---
name: rejection_wick
description: Identify rejection wicks as confirmation signals at key levels
---

# Rejection Wick Confirmation

## What is a Rejection Wick
A candle with a long wick (shadow) and small body, showing price was pushed to a level but rejected — sellers or buyers stepped in aggressively.

## Detection Rules
- Bullish rejection: long lower wick (>2x body), small body, closes near the high
- Bearish rejection: long upper wick (>2x body), small body, closes near the low
- Wick length should be at least 1 ATR to be significant

## Confirmation Usage
- At an order block: rejection wick confirms the level is defended
- At an FVG zone: rejection wick confirms institutional interest
- After a liquidity sweep: rejection wick confirms the reversal

## Invalid Rejections
- Wick in the direction of trend continuation is not a rejection
- Small wicks (less than 0.5 ATR) are noise, not signals
- Multiple rejection wicks without follow-through weakens the signal
