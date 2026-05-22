"""Typed data contracts shared across the strategy codebase."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .enums import Direction


@dataclass(frozen=True)
class FVGZone:
    """Represents a detected fair value gap zone and its metadata."""

    index: int
    timestamp: datetime
    direction: Direction
    top: float
    bottom: float


@dataclass
class TradeRecord:
    """Represents one completed or open trade lifecycle."""

    direction: Direction
    entry_time: datetime
    entry_price: float
    stop_loss: float
    take_profit: float
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None

    def risk(self) -> float:
        """Return absolute per-trade risk in price units."""
        return abs(self.entry_price - self.stop_loss)

    def r_multiple(self) -> Optional[float]:
        """Return realized R multiple once trade is closed."""
        if self.exit_price is None:
            return None
        signed_pnl = (
            self.exit_price - self.entry_price
            if self.direction == Direction.LONG
            else self.entry_price - self.exit_price
        )
        risk_value = self.risk()
        return signed_pnl / risk_value if risk_value > 0 else None

