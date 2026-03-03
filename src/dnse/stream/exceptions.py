"""Stream-specific exceptions for DNSE WebSocket streaming."""

from dnse.exceptions import DnseError


class DnseStreamError(DnseError):
    """Base exception for DNSE WebSocket streaming."""

    def __init__(self, message: str = "Stream error") -> None:
        """Initialize with optional message.

        Args:
            message: Error description.
        """
        super().__init__(message)


class DnseStreamAuthError(DnseStreamError):
    """WebSocket authentication failed."""


class DnseStreamConnectionError(DnseStreamError):
    """WebSocket connection failed or disconnected."""

    def __init__(self, message: str = "Connection error", retry_count: int = 0) -> None:
        """Initialize with message and retry count.

        Args:
            message: Error description.
            retry_count: Number of reconnect attempts made.
        """
        self.retry_count = retry_count
        super().__init__(message)


class DnseStreamProtocolError(DnseStreamError):
    """Malformed or unexpected message from server."""
