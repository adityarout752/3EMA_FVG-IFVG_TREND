"""Tests for fixed 2R risk model math."""

from src.core.enums import Direction
from src.strategy.risk_model import compute_stop_take_profit


def test_long_risk_model_2r():
    """Verify long setup generates correct 2R target."""
    sl, tp = compute_stop_take_profit(Direction.LONG, entry_price=100.0, stop_price=98.0, reward_ratio=2.0)
    assert sl == 98.0
    assert tp == 104.0


def test_short_risk_model_2r():
    """Verify short setup generates correct 2R target."""
    sl, tp = compute_stop_take_profit(Direction.SHORT, entry_price=100.0, stop_price=102.0, reward_ratio=2.0)
    assert sl == 102.0
    assert tp == 96.0

