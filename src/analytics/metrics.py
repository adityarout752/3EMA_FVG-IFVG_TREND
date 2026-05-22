"""Core backtest metrics aggregation layer."""

import numpy as np
import pandas as pd

from src.analytics.drawdown import (
    compute_drawdown_phase_count,
    compute_drawdown_series,
    compute_time_to_recover,
)
from src.analytics.streaks import compute_streak_statistics


def _profit_factor(trades_df: pd.DataFrame) -> float:
    """Compute profit factor from trade-level PnL values."""
    gross_profit = trades_df.loc[trades_df["pnl"] > 0, "pnl"].sum()
    gross_loss = -trades_df.loc[trades_df["pnl"] < 0, "pnl"].sum()
    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0
    return float(gross_profit / gross_loss)


def compute_performance_metrics(
    trades_df: pd.DataFrame,
    equity_curve: pd.Series | None = None,
) -> dict:
    """Compute required strategy KPIs from trade log and optional equity curve.

    Args:
        trades_df: Closed-trade dataframe with pnl, r_multiple, direction columns.
        equity_curve: Optional equity series for drawdown statistics.

    Returns:
        Dictionary containing performance metrics requested in blueprint.
    """
    if trades_df.empty:
        return {
            "total_trades": 0,
            "win_rate_pct": 0.0,
            "profit_factor": 0.0,
            "expectancy_r": 0.0,
            "long_trade_pct": 0.0,
            "short_trade_pct": 0.0,
            "long_win_rate_pct": 0.0,
            "short_win_rate_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "drawdown_phase_count": 0,
            "avg_bars_to_recover": float("nan"),
            "total_return_pct": 0.0,
            "sharpe_proxy": 0.0,
            **compute_streak_statistics(trades_df),
        }

    total_trades = len(trades_df)
    wins = (trades_df["pnl"] > 0).sum()
    win_rate_pct = float(wins / total_trades * 100.0)
    expectancy_r = float(trades_df["r_multiple"].dropna().mean()) if "r_multiple" in trades_df else 0.0

    long_trades = trades_df[trades_df["direction"] == "long"]
    short_trades = trades_df[trades_df["direction"] == "short"]

    total_return_pct = float(((1.0 + trades_df["return_pct"]).prod() - 1.0) * 100.0) if "return_pct" in trades_df else 0.0
    sharpe_proxy = float(np.mean(trades_df["return_pct"]) / np.std(trades_df["return_pct"])) if "return_pct" in trades_df and np.std(trades_df["return_pct"]) > 0 else 0.0

    max_drawdown_pct = 0.0
    drawdown_phase_count = 0
    avg_bars_to_recover = float("nan")
    if equity_curve is not None and not equity_curve.empty:
        drawdown = compute_drawdown_series(equity_curve)
        max_drawdown_pct = float(drawdown.min() * 100.0)
        drawdown_phase_count = compute_drawdown_phase_count(drawdown)
        avg_bars_to_recover = compute_time_to_recover(drawdown)

    return {
        "total_trades": int(total_trades),
        "win_rate_pct": win_rate_pct,
        "profit_factor": _profit_factor(trades_df),
        "expectancy_r": expectancy_r,
        "long_trade_pct": float(len(long_trades) / total_trades * 100.0),
        "short_trade_pct": float(len(short_trades) / total_trades * 100.0),
        "long_win_rate_pct": float((long_trades["pnl"] > 0).mean() * 100.0) if len(long_trades) > 0 else 0.0,
        "short_win_rate_pct": float((short_trades["pnl"] > 0).mean() * 100.0) if len(short_trades) > 0 else 0.0,
        "max_drawdown_pct": max_drawdown_pct,
        "drawdown_phase_count": int(drawdown_phase_count),
        "avg_bars_to_recover": avg_bars_to_recover,
        "total_return_pct": total_return_pct,
        "sharpe_proxy": sharpe_proxy,
        **compute_streak_statistics(trades_df),
    }

