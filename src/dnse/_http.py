"""HTTP configuration and utilities for the DNSE SDK."""

from __future__ import annotations

import json
from dataclasses import dataclass

from dnse.exceptions import DnseAPIError, DnseAuthError, DnseRateLimitError, DnseSessionExpiredError

DEFAULT_BASE_URL = "https://openapi.dnse.com.vn"

# Error codes returned by the API that indicate an expired trading token
TOKEN_EXPIRY_CODES: frozenset[str] = frozenset({"INVALID_TRADING_TOKEN"})


@dataclass(frozen=True, slots=True)
class HttpConfig:
    """Immutable HTTP client configuration."""

    base_url: str = DEFAULT_BASE_URL
    timeout: float = 30.0
    api_key: str = ""
    api_secret: str = ""
    date_header: str = "date"


def build_request_headers(
    method: str,
    path: str,
    config: HttpConfig,
) -> dict[str, str]:
    """Build per-request headers including HMAC signature when credentials are set.

    Args:
        method: HTTP method (e.g. "GET", "POST").
        path: URL path for signature (e.g. "/accounts").
        config: HTTP client configuration.

    Returns:
        Dictionary of HTTP headers for the request.
    """
    from dnse._hmac_signer import build_signature_headers

    headers: dict[str, str] = {
        "User-Agent": "dnse-python-sdk",
        "Accept": "application/json",
    }
    if config.api_key and config.api_secret:
        headers.update(
            build_signature_headers(
                method,
                path,
                config.api_key,
                config.api_secret,
                date_header=config.date_header,
            )
        )
    return headers


def handle_response(
    status_code: int,
    body: str,
    headers: dict[str, str] | None = None,
    *,
    trading_token_set: bool = False,
) -> None:
    """Map HTTP status codes to typed exceptions.

    Args:
        status_code: HTTP response status code.
        body: Response body text.
        headers: Optional response headers (used for retry-after parsing).
        trading_token_set: Whether a trading token is active on the client.
            Used to distinguish expired token (DnseSessionExpiredError) from
            bad credentials (DnseAuthError) on 401 responses.

    Raises:
        DnseSessionExpiredError: On 401 with active trading token and expiry code.
        DnseAuthError: On 401 or 403 responses.
        DnseRateLimitError: On 429 responses.
        DnseAPIError: On any other non-2xx response.
    """
    if 200 <= status_code < 300:
        return
    if status_code == 401:
        if trading_token_set:
            try:
                body_json = json.loads(body)
                error_code = body_json.get("code") or body_json.get("errorCode") or ""
                if error_code in TOKEN_EXPIRY_CODES:
                    raise DnseSessionExpiredError(status_code, body)
            except (json.JSONDecodeError, AttributeError):
                pass
        raise DnseAuthError(status_code, body)
    if status_code == 403:
        raise DnseAuthError(status_code, body)
    if status_code == 429:
        retry_after: float | None = None
        if headers and "retry-after" in headers:
            try:
                retry_after = float(headers["retry-after"])
            except (ValueError, TypeError):
                retry_after = None
        raise DnseRateLimitError(status_code, body, retry_after)
    raise DnseAPIError(status_code, body)
