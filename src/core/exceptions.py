"""Custom exceptions used by the strategy modules."""


class StrategyValidationError(ValueError):
    """Raised when strategy input data fails schema or rule validation."""


class StrategyConfigurationError(ValueError):
    """Raised when strategy configuration is incomplete or invalid."""

