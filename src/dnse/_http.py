"""HTTP configuration and utilities for the DNSE SDK."""

from __future__ import annotations

from dataclasses import dataclass

from dnse.exceptions import DnseAPIError, DnseAuthError, DnseRateLimitError


@dataclass(frozen=True, slots=True)
class HttpConfig:
    """Immutable HTTP client configuration."""

    # TODO: confirm actual DNSE Open API base URL
    base_url: str = "https://openapi.dnse.com.vn"
    timeout: float = 30.0
    api_key: str = ""


def build_headers(config: HttpConfig) -> dict[str, str]:
    """Build request headers including auth if api_key is set.

    Args:
        config: HTTP client configuration.

    Returns:
        Dictionary of HTTP headers.
    """
    headers: dict[str, str] = {
        "User-Agent": "dnse-python-sdk",
        "Accept": "application/json",
    }
    if config.api_key:
        # TODO: confirm auth header format with DNSE API docs
        headers["Authorization"] = f"Bearer {config.api_key}"
    return headers


def handle_response(
    status_code: int,
    body: str,
    headers: dict[str, str] | None = None,
) -> None:
    """Map HTTP status codes to typed exceptions.

    Args:
        status_code: HTTP response status code.
        body: Response body text.
        headers: Optional response headers (used for retry-after parsing).

    Raises:
        DnseAuthError: On 401 or 403 responses.
        DnseRateLimitError: On 429 responses.
        DnseAPIError: On any other non-2xx response.
    """
    if 200 <= status_code < 300:
        return
    if status_code in (401, 403):
        raise DnseAuthError(status_code, body)
    if status_code == 429:
        retry_after: float | None = None
        if headers and "retry-after" in headers:
            retry_after = float(headers["retry-after"])
        raise DnseRateLimitError(status_code, body, retry_after)
    raise DnseAPIError(status_code, body)
