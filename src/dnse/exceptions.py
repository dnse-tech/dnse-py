"""DNSE SDK exceptions."""


class DnseError(Exception):
    """Base exception for DNSE SDK."""


class DnseAPIError(DnseError):
    """API returned an error response."""

    def __init__(self, status_code: int, body: str) -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(f"API error {status_code}: {body}")


class DnseAuthError(DnseAPIError):
    """Authentication failed (401/403)."""


class DnseRateLimitError(DnseAPIError):
    """Rate limited (429)."""

    def __init__(self, status_code: int, body: str, retry_after: float | None = None) -> None:
        self.retry_after = retry_after
        super().__init__(status_code, body)
