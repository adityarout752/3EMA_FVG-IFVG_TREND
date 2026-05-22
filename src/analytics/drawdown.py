"""Drawdown and recovery analytics for equity-curve diagnostics."""

import numpy as np
import pandas as pd


def compute_drawdown_series(equity: pd.Series) -> pd.Series:
    """Compute drawdown series from an equity curve."""
    running_peak = equity.cummax()
    return equity / running_peak - 1.0


def compute_drawdown_phase_count(drawdown: pd.Series) -> int:
    """Count distinct drawdown phases where equity is below prior peak."""
    in_drawdown = drawdown < 0
    phase_starts = (in_drawdown & ~in_drawdown.shift(1, fill_value=False)).sum()
    return int(phase_starts)


def compute_time_to_recover(drawdown: pd.Series) -> float:
    """Compute average bars-to-recover from drawdown to flat/peak.

    Returns NaN when no complete recovery cycles exist.
    """
    in_dd = drawdown < 0
    starts = np.where(in_dd & ~in_dd.shift(1, fill_value=False))[0]
    ends = np.where(~in_dd & in_dd.shift(1, fill_value=False))[0]
    if len(starts) == 0 or len(ends) == 0:
        return float("nan")
    durations: list[int] = []
    end_ptr = 0
    for start in starts:
        while end_ptr < len(ends) and ends[end_ptr] <= start:
            end_ptr += 1
        if end_ptr < len(ends):
            durations.append(int(ends[end_ptr] - start))
    if not durations:
        return float("nan")
    return float(np.mean(durations))

