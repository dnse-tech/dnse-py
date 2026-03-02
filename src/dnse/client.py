"""Synchronous DNSE API client."""

from __future__ import annotations

from typing import Any

import httpx

from dnse._http import DEFAULT_BASE_URL, HttpConfig, build_headers, handle_response


class DnseClient:
    """Synchronous client for the DNSE Open API."""

    def __init__(
        self,
        api_key: str = "",
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        """Initialize the synchronous DNSE client.

        Args:
            api_key: Bearer token for API authentication.
            base_url: Base URL of the DNSE Open API.
            timeout: Request timeout in seconds.
        """
        self._config = HttpConfig(base_url=base_url, timeout=timeout, api_key=api_key)
        self._client = httpx.Client(
            base_url=base_url,
            headers=build_headers(self._config),
            timeout=timeout,
        )

    def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Send an HTTP request and handle errors.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: URL path relative to base_url.
            **kwargs: Additional arguments forwarded to httpx.

        Returns:
            httpx.Response on success.

        Raises:
            DnseAuthError: On 401/403 responses.
            DnseRateLimitError: On 429 responses.
            DnseAPIError: On other non-2xx responses.
        """
        response = self._client.request(method, path, **kwargs)
        handle_response(response.status_code, response.text, dict(response.headers))
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

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> DnseClient:
        """Enter context manager."""
        return self

    def __exit__(self, *args: object) -> None:
        """Exit context manager and close the client."""
        self.close()
