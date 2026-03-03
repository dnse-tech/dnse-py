"""Asynchronous DNSE API client."""

from __future__ import annotations

import asyncio
from functools import cached_property
from typing import Any

import httpx

from dnse._base_client import MAX_RETRIES, BaseClient
from dnse._http import DEFAULT_BASE_URL, HttpConfig, handle_response


class AsyncDnseClient(BaseClient):
    """Asynchronous client for the DNSE Open API (v0.2.0).

    Provides resource-oriented access to all DNSE endpoints with HMAC
    authentication, automatic 429 retry, and typed Pydantic v2 responses.

    Example::

        async with AsyncDnseClient(api_key="k", api_secret="s") as client:
            await client.registration.send_otp()
            await client.registration.verify_otp("123456")
            orders = await client.orders.list("0003979888", marketType="STOCK")
    """

    def __init__(
        self,
        api_key: str = "",
        api_secret: str = "",
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        date_header: str = "date",
    ) -> None:
        """Initialize the asynchronous DNSE client.

        Args:
            api_key: API key for HMAC authentication.
            api_secret: API secret for HMAC signing (required for authenticated calls).
            base_url: Base URL of the DNSE Open API.
            timeout: Request timeout in seconds.
            date_header: Date header name ("date" or "x-aux-date").
        """
        config = HttpConfig(
            base_url=base_url,
            timeout=timeout,
            api_key=api_key,
            api_secret=api_secret,
            date_header=date_header,
        )
        super().__init__(config)
        self._http_client = httpx.AsyncClient(base_url=base_url, timeout=timeout)

    def _send(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Not used directly — async clients use _async_send."""
        raise NotImplementedError("Use _async_send for AsyncDnseClient")

    async def _async_send(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Send an asynchronous HTTP request with per-request HMAC headers."""
        if "headers" not in kwargs:
            kwargs["headers"] = self._request_headers(method, path)
        return await self._http_client.request(method, path, **kwargs)

    async def _async_request_with_retry(
        self, method: str, path: str, **kwargs: Any
    ) -> httpx.Response:
        """Send an async request with 429 retry logic."""
        response = await self._async_send(method, path, **kwargs)
        for attempt in range(MAX_RETRIES - 1):
            delay = self._handle_retry(attempt, response)
            if delay is None:
                break
            await asyncio.sleep(delay)
            response = await self._async_send(method, path, **kwargs)
        else:
            if response.status_code == 429:
                handle_response(
                    response.status_code,
                    response.text,
                    dict(response.headers),
                    trading_token_set=self._trading_token is not None,
                )
        return response

    async def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:  # type: ignore[override]
        """Send an async HTTP request with retry and error handling."""
        response = await self._async_request_with_retry(method, path, **kwargs)
        handle_response(
            response.status_code,
            response.text,
            dict(response.headers),
            trading_token_set=self._trading_token is not None,
        )
        return response

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:  # type: ignore[override]
        """Send a GET request."""
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:  # type: ignore[override]
        """Send a POST request."""
        return await self.request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> httpx.Response:  # type: ignore[override]
        """Send a PUT request."""
        return await self.request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> httpx.Response:  # type: ignore[override]
        """Send a DELETE request."""
        return await self.request("DELETE", path, **kwargs)

    # ── Resources (lazy, cached) ──────────────────────────────────────────

    @cached_property
    def registration(self) -> AsyncRegistrationResource:
        """OTP flow resource for obtaining a trading token."""
        from dnse.resources.registration import AsyncRegistrationResource

        return AsyncRegistrationResource(self)

    @cached_property
    def accounts(self) -> AsyncAccountsResource:
        """Sub-account info, balances, loan packages, and PPSE."""
        from dnse.resources.accounts import AsyncAccountsResource

        return AsyncAccountsResource(self)

    @cached_property
    def orders(self) -> AsyncOrdersResource:
        """Order CRUD: place, list, get, update, cancel, history."""
        from dnse.resources.orders import AsyncOrdersResource

        return AsyncOrdersResource(self)

    @cached_property
    def deals(self) -> AsyncDealsResource:
        """Executed deal/position queries."""
        from dnse.resources.deals import AsyncDealsResource

        return AsyncDealsResource(self)

    @cached_property
    def market(self) -> AsyncMarketResource:
        """Market data: security definitions."""
        from dnse.resources.market import AsyncMarketResource

        return AsyncMarketResource(self)

    # ── Lifecycle ─────────────────────────────────────────────────────────

    async def aclose(self) -> None:
        """Close the underlying async HTTP client."""
        await self._http_client.aclose()

    async def __aenter__(self) -> AsyncDnseClient:
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager and close the client."""
        await self.aclose()


# Re-export resource types for TYPE_CHECKING consumers
from typing import TYPE_CHECKING  # noqa: E402

if TYPE_CHECKING:
    from dnse.resources.accounts import AsyncAccountsResource
    from dnse.resources.deals import AsyncDealsResource
    from dnse.resources.market import AsyncMarketResource
    from dnse.resources.orders import AsyncOrdersResource
    from dnse.resources.registration import AsyncRegistrationResource
