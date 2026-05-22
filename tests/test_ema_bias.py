"""Tests for EMA projection and bias engine logic."""

from src.features.bias_engine import add_bias_columns
from src.features.ema import attach_htf_ema_columns


def test_attach_htf_ema_columns(sample_ohlcv_df):
    """Verify projected EMA columns are created for all required HTFs."""
    out = attach_htf_ema_columns(sample_ohlcv_df, ema_length=10)
    assert "ema_15m" in out.columns
    assert "ema_30m" in out.columns
    assert "ema_60m" in out.columns


def test_add_bias_columns(sample_ohlcv_df):
    """Verify bias columns are added as booleans."""
    out = attach_htf_ema_columns(sample_ohlcv_df, ema_length=10)
    out = add_bias_columns(out)
    assert "long_bias" in out.columns
    assert "short_bias" in out.columns
    assert out["long_bias"].dtype == bool
    assert out["short_bias"].dtype == bool

