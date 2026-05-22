"""Fair Value Gap (FVG) detection utilities."""

import numpy as np
import pandas as pd


def add_fvg_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Detect bullish and bearish 3-candle FVG structures.

    Args:
        df: OHLCV dataframe with High and Low columns.

    Returns:
        Dataframe copy with FVG flags and zone boundaries.
    """
    out = df.copy()
    high_m2 = out["High"].shift(2)
    low_m2 = out["Low"].shift(2)

    out["bullish_fvg"] = high_m2 < out["Low"]
    out["bearish_fvg"] = low_m2 > out["High"]

    out["bullish_fvg_bottom"] = np.where(out["bullish_fvg"], high_m2, np.nan)
    out["bullish_fvg_top"] = np.where(out["bullish_fvg"], out["Low"], np.nan)

    out["bearish_fvg_bottom"] = np.where(out["bearish_fvg"], out["High"], np.nan)
    out["bearish_fvg_top"] = np.where(out["bearish_fvg"], low_m2, np.nan)
    return out

