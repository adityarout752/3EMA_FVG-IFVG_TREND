"""Shared pytest fixtures for strategy module tests."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_ohlcv_df() -> pd.DataFrame:
    """Create a small timezone-aware 5-minute OHLCV fixture."""
    idx = pd.date_range("2026-01-05 09:00:00", periods=60, freq="5min", tz="US/Eastern")
    base = np.linspace(100.0, 120.0, len(idx))
    df = pd.DataFrame(
        {
            "Open": base,
            "High": base + 1.0,
            "Low": base - 1.0,
            "Close": base + 0.2,
            "Volume": 1000,
        },
        index=idx,
    )
    return df

