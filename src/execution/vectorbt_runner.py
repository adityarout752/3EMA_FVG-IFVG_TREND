"""VectorBT execution wrapper for portfolio statistics and diagnostics."""

from typing import Any, Optional

import pandas as pd

from src.strategy.state_machine import StrategyRunResult


def run_vectorbt_portfolio(
    close: pd.Series,
    result: StrategyRunResult,
    freq: str = "5min",
) -> Optional[Any]:
    """Execute portfolio simulation from precomputed strategy signals.

    Args:
        close: Close-price series aligned to signal index.
        result: Strategy signal arrays produced by the state machine.
        freq: Frequency string for annualization/stats context.

    Returns:
        VectorBT Portfolio object if vectorbt is installed, otherwise None.
    """
    try:
        import vectorbt as vbt
    except ImportError:
        return None

    portfolio = vbt.Portfolio.from_signals(
        close=close,
        entries=result.entries_long,
        exits=result.exits_long,
        short_entries=result.entries_short,
        short_exits=result.exits_short,
        freq=freq,
    )
    return portfolio

