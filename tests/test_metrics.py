"""Tests for summary metric calculations."""

import pandas as pd

from src.analytics.metrics import compute_performance_metrics


def test_metrics_non_empty():
    """Verify core metrics return expected keys for non-empty trades."""
    trades = pd.DataFrame(
        [
            {"pnl": 2.0, "r_multiple": 1.0, "direction": "long", "return_pct": 0.02},
            {"pnl": -1.0, "r_multiple": -1.0, "direction": "short", "return_pct": -0.01},
        ]
    )
    out = compute_performance_metrics(trades)
    assert out["total_trades"] == 2
    assert "win_rate_pct" in out
    assert "profit_factor" in out

