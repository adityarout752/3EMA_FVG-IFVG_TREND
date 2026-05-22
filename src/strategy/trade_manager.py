"""Trade lifecycle utilities for candle-wise SL/TP exit evaluation."""

import pandas as pd

from src.core.enums import Direction
from src.core.types import TradeRecord


def evaluate_exit_on_bar(trade: TradeRecord, bar: pd.Series) -> tuple[bool, float, str]:
    """Evaluate whether an open trade exits on the current candle.

    Assumption:
        If both SL and TP are touched within the same candle, SL is prioritized
        for conservative backtest behavior.

    Args:
        trade: Active trade record.
        bar: Current OHLCV row containing High, Low, Close.

    Returns:
        Tuple (did_exit, exit_price, exit_reason).
    """
    high = float(bar["High"])
    low = float(bar["Low"])
    close = float(bar["Close"])

    if trade.direction == Direction.LONG:
        if low <= trade.stop_loss:
            return True, trade.stop_loss, "SL"
        if high >= trade.take_profit:
            return True, trade.take_profit, "TP"
    else:
        if high >= trade.stop_loss:
            return True, trade.stop_loss, "SL"
        if low <= trade.take_profit:
            return True, trade.take_profit, "TP"
    return False, close, ""


def force_exit_trade(trade: TradeRecord, close_price: float, reason: str) -> TradeRecord:
    """Force-close an active trade at close price for session boundary handling.

    Args:
        trade: Active trade object to close.
        close_price: Exit close price.
        reason: Exit reason label, such as SESSION_END.

    Returns:
        Updated trade record with exit details set.
    """
    trade.exit_price = close_price
    trade.exit_reason = reason
    return trade

