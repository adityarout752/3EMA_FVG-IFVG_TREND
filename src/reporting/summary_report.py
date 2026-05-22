"""Summary report builder combining metrics and seasonality outputs."""

from typing import Any

import pandas as pd

from src.analytics.metrics import compute_performance_metrics
from src.analytics.seasonality import (
    compute_win_rate_by_hour,
    compute_win_rate_by_month,
    compute_win_rate_by_weekday,
)


def build_summary_payload(
    trades_df: pd.DataFrame,
    equity_curve: pd.Series | None = None,
) -> dict[str, Any]:
    """Build report payload containing metrics and seasonality tables.

    Args:
        trades_df: Closed-trade dataframe.
        equity_curve: Optional equity curve for drawdown diagnostics.

    Returns:
        JSON-serializable dictionary with summary sections.
    """
    metrics = compute_performance_metrics(trades_df, equity_curve=equity_curve)
    by_month = compute_win_rate_by_month(trades_df).to_dict(orient="records")
    by_hour = compute_win_rate_by_hour(trades_df).to_dict(orient="records")
    by_weekday = compute_win_rate_by_weekday(trades_df).to_dict(orient="records")
    return {
        "metrics": metrics,
        "win_rate_by_month": by_month,
        "win_rate_by_hour": by_hour,
        "win_rate_by_weekday": by_weekday,
    }

