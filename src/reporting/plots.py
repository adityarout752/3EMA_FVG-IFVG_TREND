"""Plot generation utilities for equity and signal visualization."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_equity_curve(equity_curve: pd.Series, output_path: str) -> None:
    """Render and save equity curve as a PNG chart.

    Args:
        equity_curve: Time-indexed equity series.
        output_path: Destination image file path.
    """
    if equity_curve is None or equity_curve.empty:
        return
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(12, 5))
    plt.plot(equity_curve.index, equity_curve.values, label="Equity")
    plt.title("Equity Curve")
    plt.xlabel("Time")
    plt.ylabel("Equity")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def plot_price_with_entries(
    df: pd.DataFrame,
    entries_long: pd.Series,
    entries_short: pd.Series,
    output_path: str,
) -> None:
    """Render and save close price with long/short entry markers.

    Args:
        df: Feature dataframe including Close series.
        entries_long: Long-entry boolean signal series.
        entries_short: Short-entry boolean signal series.
        output_path: Destination image file path.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(14, 6))
    plt.plot(df.index, df["Close"], label="Close", linewidth=1.0)
    plt.scatter(
        df.index[entries_long],
        df.loc[entries_long, "Close"],
        label="Long Entry",
        marker="^",
    )
    plt.scatter(
        df.index[entries_short],
        df.loc[entries_short, "Close"],
        label="Short Entry",
        marker="v",
    )
    plt.title("Close With Entry Markers")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

