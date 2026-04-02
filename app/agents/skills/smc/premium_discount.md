---
name: premium_discount
description: Calculate premium and discount zones for directional bias
---

# Premium / Discount Zones

## Calculation
- Identify the current dealing range (swing high to swing low)
- Equilibrium (50%) = (swing_high + swing_low) / 2
- Premium zone: above equilibrium (50%-100%)
- Discount zone: below equilibrium (0%-50%)

## Trading Rules
- In a bullish trend: BUY in the discount zone
- In a bearish trend: SELL in the premium zone
- Avoid buying in premium or selling in discount

## Application
- Map the range on H4 or Daily for macro bias
- Entries on H1 or M15 within the correct zone
- Combine with OB/FVG inside the correct zone for highest probability
