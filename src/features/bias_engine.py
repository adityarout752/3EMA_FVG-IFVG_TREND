"""Multi-timeframe EMA bias logic used by the setup state machine."""

import pandas as pd


def add_bias_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add long/short bias flags from 5m close vs projected HTF EMAs.

    Args:
        df: Dataframe with Close, ema_15m, ema_30m, ema_60m columns.

    Returns:
        Dataframe copy with long_bias and short_bias boolean columns.
    """
    out = df.copy()
    out["long_bias"] = (
        (out["Close"] > out["ema_15m"])
        & (out["Close"] > out["ema_30m"])
        & (out["Close"] > out["ema_60m"])
    )
    out["short_bias"] = (
        (out["Close"] < out["ema_15m"])
        & (out["Close"] < out["ema_30m"])
        & (out["Close"] < out["ema_60m"])
    )
    return out

