"""Asynchronous DNSE API client."""

from __future__ import annotations

from typing import Any

import httpx

from dnse._http import HttpConfig, build_headers, handle_response


class AsyncDnseClient:
    """Asynchronous client for the DNSE Open API."""

    def __init__(
        self,
        api_key: str = "",
        *,
        base_url: str = "https://openapi.dnse.com.vn",
        timeout: float = 30.0,
    ) -> None:
        self._config = HttpConfig(base_url=base_url, timeout=timeout, api_key=api_key)
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=build_headers(self._config),
            timeout=timeout,
        )

    async def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Send an async HTTP request and handle errors.

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
        response = await self._client.request(method, path, **kwargs)
        handle_response(response.status_code, response.text, dict(response.headers))
        return response

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send a GET request."""
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send a POST request."""
        return await self.request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send a PUT request."""
        return await self.request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send a DELETE request."""
        return await self.request("DELETE", path, **kwargs)

    async def aclose(self) -> None:
        """Close the underlying async HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncDnseClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()
