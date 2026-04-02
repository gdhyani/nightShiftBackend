---
name: order_blocks
description: Identify and validate Order Blocks for potential reversal zones
---

# Order Block (OB) Identification

## What is an Order Block
The last opposing candle before a strong move that breaks structure. It represents institutional orders.

## Detection Rules
- Bullish OB: Last bearish candle before a strong bullish move that creates BOS
- Bearish OB: Last bullish candle before a strong bearish move that creates BOS
- The move after the OB must break recent structure (swing high/low)

## Validation
- OB must have caused a Break of Structure (BOS)
- OB should not have been mitigated (price returned and closed through it)
- Fresh OBs are stronger than old ones
- OBs in premium/discount zones are higher probability

## Entry Rules
- Wait for price to return to the OB zone
- Enter on confirmation (rejection candle, volume spike)
- Stop loss beyond the OB body
- Target: opposing liquidity pool or next key level
