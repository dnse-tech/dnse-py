"""Market data resource: security definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from dnse.models.market import SecurityDefinition

if TYPE_CHECKING:
    from dnse._base_client import BaseClient
    from dnse.async_client import AsyncDnseClient


class MarketResource:
    """Sync resource for market data endpoints."""

    def __init__(self, client: BaseClient) -> None:
        """Initialize with a sync client reference."""
        self._client = client

    def security_info(self, symbol: str) -> SecurityDefinition:
        """Get security definition for a symbol.

        Args:
            symbol: Security symbol (e.g. "HPG").

        Returns:
            SecurityDefinition with price limits and market info.
        """
        path = f"/price/secdef/{symbol}"
        headers = self._client._request_headers("GET", path)
        response = self._client._send("GET", path, headers=headers)
        return self._client._parse(response, SecurityDefinition)


class AsyncMarketResource:
    """Async resource for market data endpoints."""

    def __init__(self, client: AsyncDnseClient) -> None:
        """Initialize with an async client reference."""
        self._client = client

    async def security_info(self, symbol: str) -> SecurityDefinition:
        """Get security definition for a symbol (async).

        Args:
            symbol: Security symbol (e.g. "HPG").

        Returns:
            SecurityDefinition with price limits and market info.
        """
        path = f"/price/secdef/{symbol}"
        headers = self._client._request_headers("GET", path)
        response = await self._client._async_send("GET", path, headers=headers)
        return self._client._parse(response, SecurityDefinition)
