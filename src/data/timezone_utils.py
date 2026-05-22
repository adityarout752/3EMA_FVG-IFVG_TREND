"""Timezone conversion utilities for strategy session consistency."""

import pandas as pd


def ensure_timezone(df: pd.DataFrame, timezone_name: str) -> pd.DataFrame:
    """Return dataframe index converted to the target timezone.

    Args:
        df: Input dataframe indexed by timezone-aware DatetimeIndex.
        timezone_name: Target timezone name (e.g., "US/Eastern").

    Returns:
        Dataframe copied with converted timezone index.
    """
    out = df.copy()
    out.index = out.index.tz_convert(timezone_name)
    return out

