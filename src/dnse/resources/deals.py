"""Deals resource: executed deal/position queries."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dnse.models.deals import DealsResponse

if TYPE_CHECKING:
    from dnse._base_client import BaseClient
    from dnse.async_client import AsyncDnseClient


class DealsResource:
    """Sync resource for deal endpoints."""

    def __init__(self, client: BaseClient) -> None:
        """Initialize with a sync client reference."""
        self._client = client

    def list(self, account_no: str, **params: Any) -> DealsResponse:
        """Get executed deals/positions for a sub-account.

        Args:
            account_no: Sub-account number.
            **params: Optional query params (e.g. marketType, pageSize).

        Returns:
            DealsResponse with list of deal items and pagination info.
        """
        path = f"/accounts/{account_no}/deals"
        headers = self._client._request_headers("GET", path)
        response = self._client._send("GET", path, headers=headers, params=params or None)
        return self._client._parse(response, DealsResponse)


class AsyncDealsResource:
    """Async resource for deal endpoints."""

    def __init__(self, client: AsyncDnseClient) -> None:
        """Initialize with an async client reference."""
        self._client = client

    async def list(self, account_no: str, **params: Any) -> DealsResponse:
        """Get executed deals/positions for a sub-account (async).

        Args:
            account_no: Sub-account number.
            **params: Optional query params.

        Returns:
            DealsResponse with list of deal items and pagination info.
        """
        path = f"/accounts/{account_no}/deals"
        headers = self._client._request_headers("GET", path)
        response = await self._client._async_send(
            "GET", path, headers=headers, params=params or None
        )
        return self._client._parse(response, DealsResponse)
