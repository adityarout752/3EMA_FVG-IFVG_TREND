"""EMA feature generation and higher-timeframe projection helpers."""

import pandas as pd

from src.data.resampler import resample_ohlcv


def compute_ema(close: pd.Series, length: int = 50) -> pd.Series:
    """Compute exponential moving average for a close series.

    Args:
        close: Close-price series.
        length: EMA lookback length.

    Returns:
        EMA series aligned to input index.
    """
    return close.ewm(span=length, adjust=False).mean()


def attach_htf_ema_columns(
    base_df: pd.DataFrame,
    ema_length: int = 50,
) -> pd.DataFrame:
    """Attach forward-filled 15m/30m/60m EMA columns onto 5m candles.

    Args:
        base_df: Base 5-minute OHLCV dataframe.
        ema_length: EMA lookback period.

    Returns:
        Dataframe copy with ema_15m, ema_30m, ema_60m columns.
    """
    out = base_df.copy()
    htf_to_col = {"15min": "ema_15m", "30min": "ema_30m", "60min": "ema_60m"}
    for rule, col_name in htf_to_col.items():
        htf = resample_ohlcv(base_df, rule=rule)
        htf[col_name] = compute_ema(htf["Close"], length=ema_length)
        out[col_name] = htf[col_name].reindex(out.index, method="ffill")
    return out

