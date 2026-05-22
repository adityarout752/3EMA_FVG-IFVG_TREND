"""Session-window filters for restricting strategy execution times."""

import pandas as pd


def add_session_flag(
    df: pd.DataFrame,
    start_time: str = "09:00",
    end_time: str = "13:30",
) -> pd.DataFrame:
    """Add boolean session flag for rows inside intraday trading window.

    Args:
        df: Dataframe indexed by timezone-aware DatetimeIndex.
        start_time: Inclusive start (HH:MM).
        end_time: Inclusive end (HH:MM).

    Returns:
        Dataframe copy with is_session_active flag.
    """
    out = df.copy()
    out["is_session_active"] = (
        pd.Series(out.index, index=out.index).dt.time
        >= pd.to_datetime(start_time).time()
    ) & (
        pd.Series(out.index, index=out.index).dt.time
        <= pd.to_datetime(end_time).time()
    )
    return out

