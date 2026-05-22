"""Setup stage helpers for pullback-side and zone-eligibility checks."""

import pandas as pd

from src.core.enums import Direction


def is_counter_trend_pullback(
    df: pd.DataFrame,
    row_position: int,
    direction: Direction,
) -> bool:
    """Return whether the current bar behaves like a counter-trend pullback.

    Args:
        df: Feature dataframe containing at least Close values.
        row_position: Integer row position in dataframe iteration.
        direction: Active directional bias being monitored.

    Returns:
        True when a temporary counter-trend push is observed.
    """
    if row_position == 0:
        return False
    curr_close = float(df.iloc[row_position]["Close"])
    prev_close = float(df.iloc[row_position - 1]["Close"])
    if direction == Direction.LONG:
        return curr_close < prev_close
    return curr_close > prev_close


def is_counter_trend_fvg_row(row: pd.Series, direction: Direction) -> bool:
    """Return whether the row has a counter-trend FVG for the active bias.

    Args:
        row: Current candle/feature row.
        direction: Active directional bias being monitored.

    Returns:
        True when valid opposite-side FVG forms for the setup sequence.
    """
    if direction == Direction.LONG:
        return bool(row.get("bearish_fvg", False))
    return bool(row.get("bullish_fvg", False))

