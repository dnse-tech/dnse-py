"""Base client with shared retry, parsing, and header logic for DNSE SDK."""

from __future__ import annotations

import json
import logging
import re
import time
from typing import TYPE_CHECKING, Any, TypeVar

import httpx

from dnse._http import HttpConfig, build_request_headers, handle_response

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass

T = TypeVar("T")

MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0  # seconds

# The DNSE API embeds JSON objects as unescaped strings in the `metadata` field,
# e.g. "metadata": "{"key":"val"}" instead of "metadata": "{\"key\":\"val\"}".
# This regex captures the raw embedded object so we can re-encode it properly.
_RE_UNESCAPED_METADATA = re.compile(r'"metadata":\s*"(\{.*?\})"', re.DOTALL)


def _sanitize_response(text: str) -> str:
    """Fix unescaped JSON objects inside the `metadata` string field (server-side bug)."""
    return _RE_UNESCAPED_METADATA.sub(lambda m: '"metadata": ' + json.dumps(m.group(1)), text)


class BaseClient:
    """Shared logic for sync and async DNSE clients.

    Subclasses implement _send() for synchronous or asynchronous I/O.
    This class is not abstract (to avoid metaclass conflicts with cached_property).
    """

    def __init__(self, config: HttpConfig) -> None:
        """Initialize with immutable config.

        Args:
            config: HTTP client configuration including credentials.
        """
        self._config = config
        self._trading_token: str | None = None

    def set_trading_token(self, token: str) -> None:
        """Store the trading token for subsequent order mutations.

        Args:
            token: Trading token returned by the OTP verification endpoint.
        """
        self._trading_token = token

    def _request_headers(self, method: str, path: str) -> dict[str, str]:
        """Build per-request headers including HMAC signature and trading token.

        Args:
            method: HTTP method.
            path: URL path.

        Returns:
            Headers dict ready to pass to httpx.
        """
        headers = build_request_headers(method, path, self._config)
        if (
            self._trading_token
            and method.upper() in ("POST", "PUT", "DELETE")
            and "/orders" in path
        ):
            headers["trading-token"] = self._trading_token
        return headers

    def _parse(self, response: httpx.Response, model: type[T]) -> T:
        """Validate response status and parse JSON into a Pydantic model.

        Args:
            response: httpx response object.
            model: Pydantic model class to parse into.

        Returns:
            Validated model instance.

        Raises:
            DnseSessionExpiredError: On 401 with active trading token and expiry code.
            DnseAuthError: On 401/403.
            DnseRateLimitError: On 429.
            DnseAPIError: On other non-2xx status.
        """
        handle_response(
            response.status_code,
            response.text,
            dict(response.headers),
            trading_token_set=self._trading_token is not None,
        )
        logger.debug("Response body [%s]: %s", response.status_code, response.text[:200])
        text = _sanitize_response(response.text)
        return model.model_validate(json.loads(text))  # type: ignore[attr-defined]

    def _send(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Send HTTP request. Override in sync/async subclasses.

        Args:
            method: HTTP method.
            path: URL path.
            **kwargs: Additional httpx request arguments.

        Raises:
            NotImplementedError: Always — subclasses must override.
        """
        raise NotImplementedError

    def _handle_retry(self, attempt: int, response: httpx.Response) -> float | None:
        """Return sleep duration if response should be retried, else None.

        Args:
            attempt: Zero-based attempt index.
            response: The httpx response to evaluate.

        Returns:
            Seconds to wait before retry, or None if no retry needed.
        """
        if response.status_code != 429:
            return None
        raw = response.headers.get("retry-after")
        if raw:
            try:
                return float(raw)
            except (ValueError, TypeError):
                pass
        return RETRY_BASE_DELAY * (2**attempt)

    def _request_with_retry(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Send a synchronous request with 429 retry logic.

        Args:
            method: HTTP method.
            path: URL path.
            **kwargs: Additional httpx request arguments.

        Returns:
            Successful httpx.Response.

        Raises:
            DnseRateLimitError: After exhausting all retries.
        """
        response = self._send(method, path, **kwargs)
        for attempt in range(MAX_RETRIES - 1):
            delay = self._handle_retry(attempt, response)
            if delay is None:
                break
            time.sleep(delay)
            response = self._send(method, path, **kwargs)
        else:
            # Exhausted retries — let handle_response raise DnseRateLimitError
            if response.status_code == 429:
                handle_response(
                    response.status_code,
                    response.text,
                    dict(response.headers),
                    trading_token_set=self._trading_token is not None,
                )
        return response

    # Low-level HTTP methods (backward compat + used by resource classes)
    def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Send an HTTP request with retry and error handling.

        Args:
            method: HTTP method.
            path: URL path.
            **kwargs: Additional httpx request arguments.

        Returns:
            httpx.Response on success.
        """
        response = self._request_with_retry(method, path, **kwargs)
        handle_response(
            response.status_code,
            response.text,
            dict(response.headers),
            trading_token_set=self._trading_token is not None,
        )
        return response

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send a GET request."""
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send a POST request."""
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send a PUT request."""
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send a DELETE request."""
        return self.request("DELETE", path, **kwargs)
