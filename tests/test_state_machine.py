"""Tests for deterministic IFVG strategy state transitions."""

import pandas as pd

from src.strategy.state_machine import IFVGStateMachine


def test_state_machine_generates_long_trade():
    """Verify a valid long IFVG sequence produces one entry and one exit."""
    idx = pd.date_range("2026-01-06 09:00:00", periods=6, freq="5min", tz="US/Eastern")
    df = pd.DataFrame(
        {
            "Open": [100, 100, 99, 101, 103, 108],
            "High": [101, 101, 100, 103, 106, 112],
            "Low": [99, 98, 97, 100, 102, 107],
            "Close": [100, 99, 99, 102, 104, 111],
            "long_bias": [True, True, True, True, True, True],
            "short_bias": [False, False, False, False, False, False],
            "is_session_active": [True, True, True, True, True, True],
            "bearish_fvg": [False, False, True, False, False, False],
            "bullish_fvg": [False, False, False, False, False, False],
            "bearish_fvg_top": [None, None, 101.0, None, None, None],
            "bearish_fvg_bottom": [None, None, 98.0, None, None, None],
            "bullish_fvg_top": [None, None, None, None, None, None],
            "bullish_fvg_bottom": [None, None, None, None, None, None],
        },
        index=idx,
    )

    result = IFVGStateMachine(reward_ratio=2.0).run(df)
    assert result.entries_long.sum() == 1
    assert result.entries_short.sum() == 0
    assert result.exits_long.sum() == 1
    assert len(result.trades) == 1
    assert result.trades[0].exit_reason in {"TP", "END_OF_DATA", "SESSION_END"}

