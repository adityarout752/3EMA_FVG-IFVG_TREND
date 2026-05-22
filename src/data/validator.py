"""Validation helpers for input OHLCV datasets."""

import pandas as pd

from src.core.constants import REQUIRED_OHLCV_COLUMNS
from src.core.exceptions import StrategyValidationError


def validate_ohlcv_schema(df: pd.DataFrame) -> None:
    """Validate OHLCV column schema and timezone-aware index requirements.

    Args:
        df: Candle dataframe expected to contain OHLCV columns.

    Raises:
        StrategyValidationError: If required columns/index constraints fail.
    """
    missing = [col for col in REQUIRED_OHLCV_COLUMNS if col not in df.columns]
    if missing:
        raise StrategyValidationError(f"Missing required OHLCV columns: {missing}")

    if not isinstance(df.index, pd.DatetimeIndex):
        raise StrategyValidationError("Dataframe index must be a DatetimeIndex.")

    if df.index.tz is None:
        raise StrategyValidationError("DatetimeIndex must be timezone-aware.")

    if df.empty:
        raise StrategyValidationError("Input dataframe is empty.")

