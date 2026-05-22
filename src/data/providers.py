"""Market data provider adapters used by the backtest pipeline."""

from datetime import datetime

import pandas as pd
import yfinance as yf


def download_yfinance_ohlcv(
    symbol: str,
    interval: str,
    start: datetime,
    end: datetime,
) -> pd.DataFrame:
    """Download OHLCV candles from Yahoo Finance.

    Args:
        symbol: Yahoo symbol (e.g., "NQ=F").
        interval: Candle interval supported by yfinance (e.g., "5m").
        start: Inclusive UTC-ish start timestamp.
        end: Exclusive end timestamp.

    Returns:
        OHLCV dataframe with timezone-aware DatetimeIndex when available.
    """
    df = yf.download(
        tickers=symbol,
        interval=interval,
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
    )
    if df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    return df

