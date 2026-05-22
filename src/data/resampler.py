"""Resampling helpers for generating HTF candles from base timeframe data."""

import pandas as pd


def resample_ohlcv(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Resample OHLCV data to a higher timeframe using standard aggregations.

    Args:
        df: Base OHLCV dataframe indexed by DatetimeIndex.
        rule: Pandas resample rule like "15min", "30min", "60min".

    Returns:
        Resampled OHLCV dataframe with dropped incomplete rows.
    """
    agg = {
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum",
    }
    out = df.resample(rule, label="right", closed="right").agg(agg)
    return out.dropna(subset=["Open", "High", "Low", "Close"])

