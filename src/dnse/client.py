"""Synchronous DNSE API client."""

from __future__ import annotations

from functools import cached_property
from typing import Any

import httpx

from dnse._base_client import BaseClient
from dnse._http import DEFAULT_BASE_URL, HttpConfig


class DnseClient(BaseClient):
    """Synchronous client for the DNSE Open API (v0.2.0).

    Provides resource-oriented access to all DNSE endpoints with HMAC
    authentication, automatic 429 retry, and typed Pydantic v2 responses.

    Example::

        with DnseClient(api_key="k", api_secret="s") as client:
            client.registration.send_otp()
            client.registration.verify_otp("123456")
            orders = client.orders.list("0003979888", marketType="STOCK")
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
        """Initialize the synchronous DNSE client.

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
        self._http_client = httpx.Client(base_url=base_url, timeout=timeout)

    def _send(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Send a synchronous HTTP request with per-request HMAC headers."""
        if "headers" not in kwargs:
            kwargs["headers"] = self._request_headers(method, path)
        return self._http_client.request(method, path, **kwargs)

    # ── Resources (lazy, cached) ──────────────────────────────────────────

    @cached_property
    def registration(self) -> RegistrationResource:
        """OTP flow resource for obtaining a trading token."""
        from dnse.resources.registration import RegistrationResource

        return RegistrationResource(self)

    @cached_property
    def accounts(self) -> AccountsResource:
        """Sub-account info, balances, loan packages, and PPSE."""
        from dnse.resources.accounts import AccountsResource

        return AccountsResource(self)

    @cached_property
    def orders(self) -> OrdersResource:
        """Order CRUD: place, list, get, update, cancel, history."""
        from dnse.resources.orders import OrdersResource

        return OrdersResource(self)

    @cached_property
    def deals(self) -> DealsResource:
        """Executed deal/position queries."""
        from dnse.resources.deals import DealsResource

        return DealsResource(self)

    @cached_property
    def market(self) -> MarketResource:
        """Market data: security definitions."""
        from dnse.resources.market import MarketResource

        return MarketResource(self)

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http_client.close()

    def __enter__(self) -> DnseClient:
        """Enter context manager."""
        return self

    def __exit__(self, *args: object) -> None:
        """Exit context manager and close the client."""
        self.close()


# Re-export resource types for TYPE_CHECKING consumers
from typing import TYPE_CHECKING  # noqa: E402

if TYPE_CHECKING:
    from dnse.resources.accounts import AccountsResource
    from dnse.resources.deals import DealsResource
    from dnse.resources.market import MarketResource
    from dnse.resources.orders import OrdersResource
    from dnse.resources.registration import RegistrationResource
