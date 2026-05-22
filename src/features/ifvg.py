"""Inversion FVG confirmation utilities."""

import pandas as pd


def add_ifvg_confirmation_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add IFVG confirmation markers from previously formed FVG zones.

    Long IFVG confirmation:
        Close crosses above most recent bearish FVG top.
    Short IFVG confirmation:
        Close crosses below most recent bullish FVG bottom.

    Args:
        df: Dataframe with Close and FVG boundary columns.

    Returns:
        Dataframe copy with long_ifvg_confirm and short_ifvg_confirm booleans.
    """
    out = df.copy()
    out["long_ifvg_confirm"] = False
    out["short_ifvg_confirm"] = False

    active_bearish_top = None
    active_bullish_bottom = None

    for idx in out.index:
        row = out.loc[idx]
        if bool(row.get("bearish_fvg", False)):
            active_bearish_top = row["bearish_fvg_top"]
        if bool(row.get("bullish_fvg", False)):
            active_bullish_bottom = row["bullish_fvg_bottom"]

        close_price = row["Close"]
        if active_bearish_top is not None and close_price > active_bearish_top:
            out.at[idx, "long_ifvg_confirm"] = True
            active_bearish_top = None
        if active_bullish_bottom is not None and close_price < active_bullish_bottom:
            out.at[idx, "short_ifvg_confirm"] = True
            active_bullish_bottom = None

    return out

