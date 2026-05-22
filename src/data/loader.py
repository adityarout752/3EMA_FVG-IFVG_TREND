"""Data loading and preprocessing orchestration for backtest input candles."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from src.data.providers import download_yfinance_ohlcv
from src.data.timezone_utils import ensure_timezone
from src.data.validator import validate_ohlcv_schema


def load_5m_data_from_csv(path: str, timezone_name: str = "UTC") -> pd.DataFrame:
    """Load 5-minute OHLCV data from CSV with schema validation.

    Args:
        path: File path to OHLCV CSV with a datetime index column.
        timezone_name: Timezone to localize/convert index into.

    Returns:
        Validated OHLCV dataframe.
    """
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    if df.index.tz is None:
        df.index = df.index.tz_localize(timezone_name)
    else:
        df.index = df.index.tz_convert(timezone_name)
    validate_ohlcv_schema(df)
    return df


def load_5m_data_from_yfinance(
    symbol: str,
    start: datetime,
    end: datetime,
    target_timezone: str = "US/Eastern",
) -> pd.DataFrame:
    """Download and validate 5-minute OHLCV data from yfinance.

    Args:
        symbol: Yahoo Finance symbol.
        start: Start datetime for download window.
        end: End datetime for download window.
        target_timezone: Target timezone for strategy processing.

    Returns:
        Validated OHLCV dataframe converted to target timezone.
    """
    df = download_yfinance_ohlcv(symbol=symbol, interval="5m", start=start, end=end)
    validate_ohlcv_schema(df)
    return ensure_timezone(df, target_timezone)


def save_dataframe(df: pd.DataFrame, path: str) -> None:
    """Persist a dataframe to CSV on disk.

    Args:
        df: Dataframe to persist.
        path: Destination CSV path.
    """
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path)

