"""
Exception classes for BOTA force sensor driver.
"""


class BotaDriverError(Exception):
    """Base exception for BOTA driver errors."""
    pass


class BotaConnectionError(BotaDriverError):
    """Raised when connection to sensor fails."""
    pass


class BotaTimeoutError(BotaDriverError):
    """Raised when communication timeout occurs."""
    pass


class BotaConfigError(BotaDriverError):
    """Raised when sensor configuration is invalid."""
    pass


class BotaDataError(BotaDriverError):
    """Raised when data parsing fails."""
    pass
