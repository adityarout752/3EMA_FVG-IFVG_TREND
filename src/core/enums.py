"""Enumerations for strategy state and directional semantics."""

from enum import Enum


class Bias(str, Enum):
    """Represents the active market bias derived from HTF EMA alignment."""

    LONG = "long"
    SHORT = "short"
    NONE = "none"


class Direction(str, Enum):
    """Represents trade direction."""

    LONG = "long"
    SHORT = "short"


class StrategyState(str, Enum):
    """Represents the deterministic IFVG strategy lifecycle states."""

    WAIT_BIAS = "WAIT_BIAS"
    WAIT_PULLBACK = "WAIT_PULLBACK"
    WAIT_BEARISH_FVG = "WAIT_BEARISH_FVG"
    WAIT_BULLISH_FVG = "WAIT_BULLISH_FVG"
    WAIT_IFVG_CONFIRMATION = "WAIT_IFVG_CONFIRMATION"
    MANAGE_TRADE = "MANAGE_TRADE"

