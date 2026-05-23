"""Data loading and preprocessing orchestration for backtest input candles."""

from datetime import datetime
import os
from pathlib import Path

import pandas as pd

from src.data.providers import download_mt5_ohlcv, download_yfinance_ohlcv
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


def load_5m_data_from_mt5(
    symbol: str,
    start: datetime,
    end: datetime,
    target_timezone: str = "US/Eastern",
    login: int | None = None,
    password: str | None = None,
    server: str | None = None,
    terminal_path: str | None = None,
) -> pd.DataFrame:
    """Download and validate 5-minute OHLCV data from MT5/FTMO server.

    Args:
        symbol: MT5 symbol name (e.g., "US100.cash").
        start: Start datetime for download window.
        end: End datetime for download window.
        target_timezone: Target timezone for strategy processing.
        login: Optional account login id.
        password: Optional account password.
        server: Optional broker server name.
        terminal_path: Optional terminal executable path.

    Returns:
        Validated OHLCV dataframe converted to target timezone.
    """
    df = download_mt5_ohlcv(
        symbol=symbol,
        start=start,
        end=end,
        timeframe_name="M5",
        login=login,
        password=password,
        server=server,
        terminal_path=terminal_path,
    )
    validate_ohlcv_schema(df)
    return ensure_timezone(df, target_timezone)


def resolve_mt5_credentials(data_cfg: dict) -> dict:
    """Resolve MT5 credentials from config first, then environment.

    Expected env keys:
        FTMO_LOGIN, FTMO_PASSWORD, FTMO_SERVER, MT5_TERMINAL_PATH
    """
    def _pick(cfg_key: str, env_key: str) -> str:
        cfg_val = data_cfg.get(cfg_key, None)
        if cfg_val is not None and str(cfg_val).strip() != "":
            return str(cfg_val).strip()
        return os.getenv(env_key, "").strip()

    login_raw = _pick("login", "FTMO_LOGIN")
    login = int(login_raw) if login_raw else None
    password = _pick("password", "FTMO_PASSWORD")
    server = _pick("server", "FTMO_SERVER")
    terminal_path = _pick("terminal_path", "MT5_TERMINAL_PATH")
    return {
        "login": login,
        "password": password or None,
        "server": server or None,
        "terminal_path": terminal_path or None,
    }


def save_dataframe(df: pd.DataFrame, path: str) -> None:
    """Persist a dataframe to CSV on disk.

    Args:
        df: Dataframe to persist.
        path: Destination CSV path.
    """
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path)
