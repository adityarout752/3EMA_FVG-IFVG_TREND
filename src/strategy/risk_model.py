"""Risk-model helpers for stop, target, and R-multiple calculations."""

from typing import Tuple

from src.core.enums import Direction


def compute_stop_take_profit(
    direction: Direction,
    entry_price: float,
    stop_price: float,
    reward_ratio: float = 2.0,
) -> Tuple[float, float]:
    """Compute stop and target for a fixed-RR trade model.

    Args:
        direction: Trade direction.
        entry_price: Fill/entry price.
        stop_price: Fixed stop-loss price.
        reward_ratio: Target reward multiple (default 2R).

    Returns:
        Tuple of (stop_loss, take_profit).

    Raises:
        ValueError: If the computed risk is non-positive.
    """
    risk = abs(entry_price - stop_price)
    if risk <= 0:
        raise ValueError("Risk must be positive for SL/TP computation.")
    if direction == Direction.LONG:
        return stop_price, entry_price + reward_ratio * risk
    return stop_price, entry_price - reward_ratio * risk

