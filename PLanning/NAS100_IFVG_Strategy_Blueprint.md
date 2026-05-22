# NAS100 IFVG + Multi-TF EMA Strategy Blueprint

## Overview

This document defines the full architecture for a **NAS100 / NQ Intraday IFVG Continuation Strategy** designed for implementation in:

- Python
- vectorbt
- pandas
- AI coding agents
- autonomous strategy builders

The goal is to provide a **fully deterministic strategy specification** so any coding model can implement the strategy consistently.

---

# Core Concept

The strategy combines:

1. Multi-timeframe trend alignment
2. Liquidity pullback
3. Fair Value Gap (FVG)
4. Inversion Fair Value Gap (IFVG)
5. Continuation entry with 2R targeting

The strategy trades ONLY in the direction of higher timeframe momentum.

---

# Trading Instrument

## Primary Instrument

```text
NAS100
```

Possible Data Sources:

| Provider | Ticker |
|---|---|
| Yahoo Finance | NQ=F |
| Yahoo Finance | ^NDX |
| Broker Feed | US100.cash |

---

# Timeframes

## Base Trading Timeframe

```text
5 Minute
```

All entries execute on:

```text
5m candles
```

---

## Higher Timeframes

Derived from 5m data:

| TF | Purpose |
|---|---|
| 15m | Intermediate trend |
| 30m | Macro intraday trend |
| 60m | Session directional bias |

---

# Data Pipeline

## Step 1 — Download Data

Required columns:

```python
Open
High
Low
Close
Volume
```

Index must be timezone-aware.

---

## Step 2 — Resample Higher Timeframes

From 5m dataframe:

```python
15m
30m
60m
```

using:

```python
df.resample()
```

---

## Step 3 — Compute EMA

Compute:

```text
EMA 50
```

for:

- 5m
- 15m
- 30m
- 60m

---

## Step 4 — Forward Fill HTF EMA

Forward-fill all HTF EMA values back onto 5m index.

Final dataframe contains:

```python
ema_15m
ema_30m
ema_60m
```

for every 5m candle.

---

# Multi-Timeframe Bias Engine

## Long Bias

Long bias becomes active when:

```python
close > ema_15m
AND
close > ema_30m
AND
close > ema_60m
```

---

## Short Bias

Short bias becomes active when:

```python
close < ema_15m
AND
close < ema_30m
AND
close < ema_60m
```

---

# Session Filter

Convert timestamps to:

```python
US/Eastern
```

Only allow setups during:

```text
09:00 AM → 01:30 PM ET
```

No trades outside this window.

---

# Pullback Logic

The strategy DOES NOT chase breakouts.

After trend alignment:

- wait for temporary counter-trend move
- look for liquidity sweep
- then search for IFVG continuation

---

# Swing Detection

## Swing Low

For longs:

```python
rolling_low = low.rolling(N).min()
```

A pullback exists when:

```python
price dips below recent swing low
```

---

## Swing High

For shorts:

```python
rolling_high = high.rolling(N).max()
```

A pullback exists when:

```python
price rises above recent swing high
```

---

# Fair Value Gap (FVG)

## Definition

3-candle imbalance structure.

---

## Bullish FVG

```python
high[i-2] < low[i]
```

Gap exists between:

```text
Candle1 High
AND
Candle3 Low
```

---

## Bearish FVG

```python
low[i-2] > high[i]
```

Gap exists between:

```text
Candle1 Low
AND
Candle3 High
```

---

# Important Rule

FVG must form:

```text
during or after pullback
```

NOT randomly.

---

# IFVG (Inversion Fair Value Gap)

This is the actual trigger model.

---

# Long IFVG Entry

## Sequence

1. Long bias active
2. Pullback occurs
3. Bearish FVG forms during pullback
4. Price closes BACK ABOVE bearish FVG
5. FVG flips bullish
6. Enter long

---

## Entry Price

```python
entry = close_of_inversion_candle
```

---

## Stop Loss

Bottom of bearish FVG.

---

## Take Profit

```python
TP = Entry + 2 * Risk
```

---

# Short IFVG Entry

## Sequence

1. Short bias active
2. Pullback occurs
3. Bullish FVG forms during pullback
4. Price closes BELOW bullish FVG
5. FVG flips bearish
6. Enter short

---

## Entry Price

```python
entry = close_of_inversion_candle
```

---

## Stop Loss

Top of bullish FVG.

---

## Take Profit

```python
TP = Entry - 2 * Risk
```

---

# Trade Lifecycle State Machine

The system should internally track setup state.

---

## Long State Sequence

```text
WAIT_BIAS
→ WAIT_PULLBACK
→ WAIT_BEARISH_FVG
→ WAIT_IFVG_CONFIRMATION
→ ENTER_LONG
→ MANAGE_TRADE
→ EXIT
```

---

## Short State Sequence

```text
WAIT_BIAS
→ WAIT_PULLBACK
→ WAIT_BULLISH_FVG
→ WAIT_IFVG_CONFIRMATION
→ ENTER_SHORT
→ MANAGE_TRADE
→ EXIT
```

---

# Risk Management

## Risk Reward

```text
1 : 2
```

Fixed.

---

## One Trade At A Time

Only one active trade allowed.

---

## Optional Future Filters

Potential additions:

- ATR filter
- News filter
- AVWAP alignment
- Session VWAP
- SMT divergence
- Volume spike confirmation
- EMA slope filter

---

# VectorBT Implementation Layer

## Execution Engine

Use:

```python
vbt.Portfolio.from_signals()
```

---

## Required Arrays

### Entries

```python
entries_long
entries_short
```

### Exits

```python
exits_long
exits_short
```

### SL

Per-trade SL arrays.

### TP

Per-trade TP arrays.

---

# Important Engineering Note

This strategy is:

```text
event-sequence driven
```

NOT simple indicator crossover logic.

Recommended architecture:

```text
pandas state engine
+
vectorbt execution/statistics
```

instead of pure vectorization.

---

# Required Outputs

## Performance Metrics

- Win rate
- Sharpe ratio
- Profit factor
- Max drawdown
- Total return
- Expectancy

---

## Trade Log

Per-trade:

| Field |
|---|
| Entry Time |
| Entry Price |
| Stop Loss |
| Take Profit |
| Exit Time |
| Exit Price |
| R Multiple |
| PnL |
| Direction |

---

## Visual Outputs

- Equity curve
- Trade markers
- FVG visualization
- EMA overlay
- IFVG confirmation

---

# Chart Example 1 — Long IFVG Continuation

This example shows:

- Multi-TF EMA alignment
- Pullback into bearish FVG
- IFVG inversion
- 2R continuation move

![Chart Example 1](Screenshot%202026-05-22%20213725.png)

---

# Chart Example 2 — IFVG Structure Visualization

This example highlights:

- Bearish FVG zone
- Inversion confirmation
- Entry
- Stop loss
- 2R target

![Chart Example 2](Screenshot%202026-05-22%20213741.png)

---

# Strategy Philosophy

This strategy attempts to trade:

```text
institutional continuation after liquidity sweep
```

using:

- higher timeframe trend
- imbalance inefficiency
- failed pullback continuation
- displacement confirmation

The IFVG acts as:

```text
a failed counter-trend imbalance
```

which often signals continuation.

---

# Final Notes

This document is intended to be:

- deterministic
- AI-agent friendly
- implementation-ready
- unambiguous
- modular

Any coding model implementing this strategy should preserve:

1. setup sequencing
2. IFVG inversion logic
3. multi-timeframe EMA alignment
4. session filter
5. fixed 2R risk model
