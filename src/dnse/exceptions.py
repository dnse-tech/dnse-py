"""DNSE SDK exceptions."""


class DnseError(Exception):
    """Base exception for DNSE SDK."""


class DnseAPIError(DnseError):
    """API returned an error response."""

    def __init__(self, status_code: int, body: str) -> None:
        """Initialize with HTTP status code and response body.

        Args:
            status_code: HTTP response status code.
            body: Response body text.
        """
        self.status_code = status_code
        self.body = body
        super().__init__(f"API error {status_code}: {body}")


class DnseAuthError(DnseAPIError):
    """Authentication failed (401/403)."""


class DnseRateLimitError(DnseAPIError):
    """Rate limited (429)."""

    def __init__(self, status_code: int, body: str, retry_after: float | None = None) -> None:
        """Initialize with status code, body, and optional retry-after seconds.

        Args:
            status_code: HTTP response status code (429).
            body: Response body text.
            retry_after: Seconds to wait before retrying, if provided by server.
        """
        self.retry_after = retry_after
        super().__init__(status_code, body)
