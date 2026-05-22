"""Tests for FVG and IFVG feature generation."""

import pandas as pd

from src.features.fvg import add_fvg_columns
from src.features.ifvg import add_ifvg_confirmation_columns


def test_fvg_columns_exist(sample_ohlcv_df):
    """Verify expected FVG feature columns are created."""
    out = add_fvg_columns(sample_ohlcv_df)
    expected = {
        "bullish_fvg",
        "bearish_fvg",
        "bullish_fvg_bottom",
        "bullish_fvg_top",
        "bearish_fvg_bottom",
        "bearish_fvg_top",
    }
    assert expected.issubset(set(out.columns))


def test_ifvg_columns_exist(sample_ohlcv_df):
    """Verify IFVG confirmation columns are present and boolean."""
    out = add_fvg_columns(sample_ohlcv_df)
    out = add_ifvg_confirmation_columns(out)
    assert "long_ifvg_confirm" in out.columns
    assert "short_ifvg_confirm" in out.columns
    assert pd.api.types.is_bool_dtype(out["long_ifvg_confirm"])
    assert pd.api.types.is_bool_dtype(out["short_ifvg_confirm"])

