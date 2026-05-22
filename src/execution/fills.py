"""Fill-model placeholders for future slippage/spread enhancements."""


def identity_fill(price: float) -> float:
    """Return unchanged fill price (no slippage model)."""
    return price

