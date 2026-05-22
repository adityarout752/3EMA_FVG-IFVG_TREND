"""Trade log materialization from in-memory TradeRecord objects."""

import pandas as pd

from src.core.types import TradeRecord


def build_trade_log(trades: list[TradeRecord]) -> pd.DataFrame:
    """Convert strategy trade objects into a normalized dataframe.

    Args:
        trades: List of completed trade records.

    Returns:
        Dataframe with required per-trade output fields.
    """
    rows = []
    for trade in trades:
        if trade.exit_price is None or trade.exit_time is None:
            continue
        pnl = (
            trade.exit_price - trade.entry_price
            if trade.direction.value == "long"
            else trade.entry_price - trade.exit_price
        )
        ret = pnl / trade.entry_price if trade.entry_price != 0 else 0.0
        rows.append(
            {
                "entry_time": trade.entry_time,
                "entry_price": trade.entry_price,
                "stop_loss": trade.stop_loss,
                "take_profit": trade.take_profit,
                "exit_time": trade.exit_time,
                "exit_price": trade.exit_price,
                "r_multiple": trade.r_multiple(),
                "pnl": pnl,
                "return_pct": ret,
                "direction": trade.direction.value,
                "exit_reason": trade.exit_reason,
            }
        )
    return pd.DataFrame(rows)

