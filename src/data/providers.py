"""Market data provider adapters used by the backtest pipeline."""

from datetime import datetime, timezone

import pandas as pd
import yfinance as yf


def _to_utc(dt: datetime) -> datetime:
    """Convert datetime to timezone-aware UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


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


def download_mt5_ohlcv(
    symbol: str,
    start: datetime,
    end: datetime,
    timeframe_name: str = "M5",
    login: int | None = None,
    password: str | None = None,
    server: str | None = None,
    terminal_path: str | None = None,
) -> pd.DataFrame:
    """Download OHLCV candles from MetaTrader 5 (FTMO demo compatible).

    Args:
        symbol: MT5 symbol (e.g., "US100.cash").
        start: Inclusive start datetime.
        end: Exclusive end datetime.
        timeframe_name: MT5 timeframe key, default "M5".
        login: MT5 account login number.
        password: MT5 account password.
        server: MT5 broker server name (e.g., "FTMO-Demo").
        terminal_path: Optional path to terminal executable.

    Returns:
        Dataframe with standardized OHLCV columns and UTC DatetimeIndex.

    Raises:
        RuntimeError: If MT5 cannot initialize/login/fetch rates.
        ValueError: If timeframe name is unsupported.
    """
    try:
        import MetaTrader5 as mt5
    except ImportError as exc:
        raise RuntimeError(
            "MetaTrader5 package not installed. Run: pip install MetaTrader5"
        ) from exc

    tf_map = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
    }
    if timeframe_name not in tf_map:
        raise ValueError(f"Unsupported MT5 timeframe: {timeframe_name}")

    init_ok = mt5.initialize(path=terminal_path) if terminal_path else mt5.initialize()
    if not init_ok:
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

    try:
        if login is not None and password and server:
            auth_ok = mt5.login(login=int(login), password=password, server=server)
            if not auth_ok:
                raise RuntimeError(f"MT5 login failed: {mt5.last_error()}")

        start_utc = _to_utc(start)
        end_utc = _to_utc(end)
        rates = mt5.copy_rates_range(symbol, tf_map[timeframe_name], start_utc, end_utc)
        if rates is None or len(rates) == 0:
            raise RuntimeError(
                f"No MT5 candles returned for symbol={symbol}, range={start_utc}..{end_utc}."
            )

        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        df = df.set_index("time")
        df = df.rename(
            columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "tick_volume": "Volume",
            }
        )
        return df[["Open", "High", "Low", "Close", "Volume"]]
    finally:
        mt5.shutdown()
