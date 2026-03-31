"""Market data resource: security definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from dnse._http import handle_response
from dnse.models.market import BoardId, SecurityDefinition

if TYPE_CHECKING:
    from dnse._base_client import BaseClient
    from dnse.async_client import AsyncDnseClient


def _parse_secdef_list(body: object) -> list[SecurityDefinition]:
    """Unwrap server list response into SecurityDefinition instances."""
    items = body if isinstance(body, list) else [body]
    return [SecurityDefinition.model_validate(item) for item in items]


class MarketResource:
    """Sync resource for market data endpoints."""

    def __init__(self, client: BaseClient) -> None:
        """Initialize with a sync client reference."""
        self._client = client

    def security_info(
        self,
        symbol: str,
        board_id: BoardId | None = None,
    ) -> list[SecurityDefinition]:
        """Get security definition(s) for a symbol.

        Args:
            symbol: Security symbol (e.g. "HPG").
            board_id: Optional board filter. Omit to get all boards for the symbol.

        Returns:
            List of SecurityDefinition — one entry per board.
        """
        path = f"/price/{symbol}/secdef"
        params = {"boardId": board_id.value} if board_id else {}
        headers = self._client._request_headers("GET", path)
        response = self._client._send("GET", path, headers=headers, params=params)
        handle_response(
            response.status_code,
            response.text,
            dict(response.headers),
            trading_token_set=self._client._trading_token is not None,
        )
        return _parse_secdef_list(response.json())


class AsyncMarketResource:
    """Async resource for market data endpoints."""

    def __init__(self, client: AsyncDnseClient) -> None:
        """Initialize with an async client reference."""
        self._client = client

    async def security_info(
        self,
        symbol: str,
        board_id: BoardId | None = None,
    ) -> list[SecurityDefinition]:
        """Get security definition(s) for a symbol (async).

        Args:
            symbol: Security symbol (e.g. "HPG").
            board_id: Optional board filter. Omit to get all boards for the symbol.

        Returns:
            List of SecurityDefinition — one entry per board.
        """
        path = f"/price/{symbol}/secdef"
        params = {"boardId": board_id.value} if board_id else {}
        headers = self._client._request_headers("GET", path)
        response = await self._client._async_send("GET", path, headers=headers, params=params)
        handle_response(
            response.status_code,
            response.text,
            dict(response.headers),
            trading_token_set=self._client._trading_token is not None,
        )
        return _parse_secdef_list(response.json())
