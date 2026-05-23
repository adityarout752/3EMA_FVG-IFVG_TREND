"""Tests for HTML report generation."""

import pandas as pd

from src.reporting.html_report import build_html_report


def test_build_html_report_creates_file(tmp_path):
    """Verify HTML report file is generated with expected content markers."""
    summary = {
        "metrics": {"total_trades": 2, "win_rate_pct": 50.0},
        "win_rate_by_month": [{"month": "2026-01", "win_rate_pct": 50.0}],
        "win_rate_by_hour": [{"hour": 10, "win_rate_pct": 100.0}],
        "win_rate_by_weekday": [{"weekday": "Monday", "win_rate_pct": 100.0}],
        "monte_carlo": {"mean": {"total_return_pct": 1.2}},
    }
    trades = pd.DataFrame([{"entry_time": "2026-01-01", "pnl": 1.0, "direction": "long"}])
    mc = pd.DataFrame([{"scenario": 1, "total_return_pct": 1.5}])
    output = tmp_path / "report.html"

    build_html_report(summary, trades, mc, str(output))

    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "NAS100 IFVG Backtest Report" in content
    assert "Trade Log (Full)" in content
    assert "Monte Carlo Scenarios (Full)" in content

