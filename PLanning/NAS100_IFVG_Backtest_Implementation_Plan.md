# NAS100 IFVG Backtest Implementation Plan

## Goal
Build a deterministic, modular, and production-style backtest system for the **NAS100 IFVG + Multi-TF EMA Continuation Strategy** using Python, pandas, and vectorbt, with strict separation of concerns and method-level documentation.

---

## 1. Project Structure

```text
3EMA_FVG_+IFVG_TREND_CONTINUTION/
  README.md
  requirements.txt
  .env.example

  config/
    strategy.yaml
    logging.yaml

  data/
    raw/
    processed/

  output/
    reports/
    charts/
    trades/

  src/
    __init__.py

    core/
      __init__.py
      types.py
      enums.py
      constants.py
      exceptions.py

    data/
      __init__.py
      providers.py
      loader.py
      validator.py
      resampler.py
      timezone_utils.py

    features/
      __init__.py
      ema.py
      bias_engine.py
      session_filter.py
      fvg.py
      ifvg.py

    strategy/
      __init__.py
      state_machine.py
      setup_detector.py
      signal_builder.py
      risk_model.py
      trade_manager.py

    execution/
      __init__.py
      vectorbt_runner.py
      fills.py

    analytics/
      __init__.py
      metrics.py
      monte_carlo.py
      drawdown.py
      seasonality.py
      streaks.py

    reporting/
      __init__.py
      trade_log.py
      summary_report.py
      plots.py
      exporter.py

    app/
      __init__.py
      run_backtest.py
      run_batch.py

  tests/
    conftest.py
    test_resampler.py
    test_ema_bias.py
    test_fvg_ifvg.py
    test_state_machine.py
    test_risk_model.py
    test_signals.py
    test_metrics.py

  notebooks/
    exploration.ipynb
```

---

## 2. Coding Standards

- Use `PEP8` + type hints everywhere.
- Use `dataclasses` for immutable strategy objects (`frozen=True` where applicable).
- Keep functions pure where possible (input -> output, no side effects).
- Do not mix I/O with business logic.
- Use structured logging (no random prints in modules).
- Keep constants in one place (`core/constants.py`).
- Use explicit timezone-aware datetime operations only.
- One module = one responsibility.

---

## 3. Method Comment Standard

Every public method should include:

- Purpose (`what` it does)
- Key assumptions (`input expectations`)
- Returns (`shape/type and meaning`)
- Side effects (if any)

Docstring template:

```python
def method_name(arg1: pd.DataFrame) -> pd.DataFrame:
    """Compute <feature_name> for the provided candle data.

    Args:
        arg1: OHLCV dataframe indexed by timezone-aware DatetimeIndex.

    Returns:
        DataFrame aligned to input index with computed feature columns.

    Raises:
        ValueError: If required columns are missing.
    """
```

---

## 4. Separation of Concerns (SoC)

- `data/*`: only ingestion, validation, resampling, timezone normalization.
- `features/*`: only feature calculation (EMA, FVG, IFVG, bias flags).
- `strategy/*`: only event-sequence logic (state machine + entries/exits + SL/TP).
- `execution/*`: only vectorbt integration/execution arrays.
- `analytics/*`: only post-backtest stats and derived KPIs.
- `reporting/*`: only output artifacts (csv/json/charts/html).
- `app/*`: only orchestration scripts / CLI entry points.

---

## 5. Implementation Phases

## Phase 1: Data & Timeframe Foundation

1. Build data loader for 5m OHLCV.
2. Enforce schema validation:
   - required columns: `Open, High, Low, Close, Volume`
   - timezone-aware index mandatory
3. Convert index to `US/Eastern`.
4. Resample 5m -> 15m, 30m, 60m.
5. Persist processed dataset to `data/processed/`.

Deliverable: validated multi-timeframe dataframe pipeline.

## Phase 2: Feature Layer

1. Compute EMA50 on 15m/30m/60m.
2. Forward-fill HTF EMA columns onto 5m index:
   - `ema_15m`, `ema_30m`, `ema_60m`
3. Create bias flags:
   - `long_bias = close > all_3_emas`
   - `short_bias = close < all_3_emas`
4. Session window flag:
   - active only `09:00` to `13:30` ET

Deliverable: feature-enriched 5m dataframe.

## Phase 3: FVG + IFVG Engine

1. Implement bullish FVG: `high[i-2] < low[i]`.
2. Implement bearish FVG: `low[i-2] > high[i]`.
3. Store zone boundaries and formation index/time.
4. Tag pullback-side FVG only (counter-trend side rule).
5. Implement IFVG inversion confirmation:
   - long: close back above bearish FVG zone
   - short: close back below bullish FVG zone

Deliverable: deterministic setup candidates with valid IFVG triggers.

## Phase 4: Event-Driven State Machine

Implement explicit states:

- `WAIT_BIAS`
- `WAIT_PULLBACK`
- `WAIT_BEARISH_FVG` / `WAIT_BULLISH_FVG`
- `WAIT_IFVG_CONFIRMATION`
- `ENTER_LONG` / `ENTER_SHORT`
- `MANAGE_TRADE`
- `EXIT`

Rules:

- one trade at a time
- fixed RR = 1:2
- long SL = bottom of bearish FVG
- short SL = top of bullish FVG
- entry = inversion candle close

Deliverable: reliable entries/exits + sl/tp arrays.

## Phase 5: VectorBT Execution

1. Build `entries_long`, `entries_short`, `exits_long`, `exits_short`.
2. Build per-trade SL/TP aligned arrays.
3. Run `vbt.Portfolio.from_signals()`.
4. Cross-check trade count with state-machine logs.

Deliverable: reproducible portfolio results.

## Phase 6: Analytics & Reporting

Compute required outputs:

- win rate
- sharpe ratio
- profit factor
- max drawdown
- total return
- expectancy
- monte carlo scenario
- win rate by month
- win rate by hour
- win rate by day
- time to recover drawdown
- number of drawdown phases
- max/avg consecutive wins/losses
- long vs short % and win rate

Trade log columns:

- Entry Time, Entry Price
- Stop Loss, Take Profit
- Exit Time, Exit Price
- R Multiple, PnL, Direction

Visuals:

- equity curve
- trade markers
- FVG zones
- EMA overlay
- IFVG confirmation markers

Deliverable: CSV + plots + summary report.

## Phase 7: Testing & Validation

1. Unit tests for each module.
2. State-machine scenario tests using synthetic candles.
3. Regression test with fixed sample data.
4. Sanity checks:
   - no lookahead bias
   - no timezone drift
   - one-trade-at-a-time constraint respected

Deliverable: stable, verifiable backtest system.

---

## 6. Definition of Done

- Strategy rules from blueprint mapped 1:1 to code.
- All outputs generated without manual intervention.
- Tests pass for core logic.
- Code is modular, documented, and maintainable.
- Backtest run is reproducible via single command.

---

## 7. Recommended Execution Order (Practical)

1. `data` modules
2. `features` modules
3. `strategy` state engine
4. `execution` vectorbt bridge
5. `analytics` + `reporting`
6. tests and validation

---

## 8. Future Enhancements (Post-v1)

- Slippage and spread modeling by session volatility.
- Parameter sweeps for EMA length and RR.
- Walk-forward validation.
- Multi-asset support with same engine.
- Live paper-trading adapter.

---

## 9. Notes for Clean Collaboration

- Keep every module under 300 lines where practical.
- Prefer small composable functions over long methods.
- Add changelog entries for rule changes.
- Lock deterministic behavior with fixed test fixtures.

This plan is implementation-ready and aligned with your blueprint, coding standards, comments requirement, and separation-of-concerns expectation.
