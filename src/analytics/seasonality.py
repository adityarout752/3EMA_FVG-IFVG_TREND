"""Seasonality analytics over closed-trade performance dimensions."""

import pandas as pd


def compute_win_rate_by_month(trades_df: pd.DataFrame) -> pd.DataFrame:
    """Compute monthly win rate percentage from trade log."""
    if trades_df.empty:
        return pd.DataFrame(columns=["month", "win_rate_pct"])
    temp = trades_df.copy()
    temp["month"] = pd.to_datetime(temp["entry_time"]).dt.to_period("M").astype(str)
    out = temp.groupby("month")["pnl"].apply(lambda s: (s > 0).mean() * 100.0).reset_index()
    return out.rename(columns={"pnl": "win_rate_pct"})


def compute_win_rate_by_hour(trades_df: pd.DataFrame) -> pd.DataFrame:
    """Compute hour-of-day win rate percentage from trade log."""
    if trades_df.empty:
        return pd.DataFrame(columns=["hour", "win_rate_pct"])
    temp = trades_df.copy()
    temp["hour"] = pd.to_datetime(temp["entry_time"]).dt.hour
    out = temp.groupby("hour")["pnl"].apply(lambda s: (s > 0).mean() * 100.0).reset_index()
    return out.rename(columns={"pnl": "win_rate_pct"})


def compute_win_rate_by_weekday(trades_df: pd.DataFrame) -> pd.DataFrame:
    """Compute weekday win rate percentage from trade log."""
    if trades_df.empty:
        return pd.DataFrame(columns=["weekday", "win_rate_pct"])
    temp = trades_df.copy()
    temp["weekday"] = pd.to_datetime(temp["entry_time"]).dt.day_name()
    out = temp.groupby("weekday")["pnl"].apply(lambda s: (s > 0).mean() * 100.0).reset_index()
    return out.rename(columns={"pnl": "win_rate_pct"})

