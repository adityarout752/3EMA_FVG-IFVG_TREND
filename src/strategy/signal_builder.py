"""Signal serialization helpers for execution and reporting layers."""

import pandas as pd

from src.strategy.state_machine import StrategyRunResult


def signals_to_dataframe(result: StrategyRunResult) -> pd.DataFrame:
    """Convert strategy run result into a single aligned signal dataframe.

    Args:
        result: State machine output containing signal series.

    Returns:
        Dataframe with entry/exit booleans and per-entry SL/TP columns.
    """
    return pd.DataFrame(
        {
            "entries_long": result.entries_long,
            "entries_short": result.entries_short,
            "exits_long": result.exits_long,
            "exits_short": result.exits_short,
            "stop_loss": result.stop_loss,
            "take_profit": result.take_profit,
        }
    )

