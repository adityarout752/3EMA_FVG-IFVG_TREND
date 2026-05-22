"""Tests for OHLCV resampling behavior."""

from src.data.resampler import resample_ohlcv


def test_resample_15min_produces_rows(sample_ohlcv_df):
    """Verify 5-minute candles resample into non-empty 15-minute candles."""
    out = resample_ohlcv(sample_ohlcv_df, "15min")
    assert not out.empty
    assert set(["Open", "High", "Low", "Close", "Volume"]).issubset(out.columns)

