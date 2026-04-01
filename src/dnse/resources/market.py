"""Market data resource: security definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from dnse._http import handle_response
from dnse.models.market import BoardId, SecurityDefinition, Trade

if TYPE_CHECKING:
    from dnse._base_client import BaseClient
    from dnse.async_client import AsyncDnseClient


def _parse_secdef_list(body: object) -> list[SecurityDefinition]:
    """Unwrap server list response into SecurityDefinition instances."""
    items = cast(list[Any], body if isinstance(body, list) else [body])
    return [SecurityDefinition.model_validate(item) for item in items]


def _parse_trade_list(body: object) -> list[Trade]:
    """Unwrap {"trades": [...]} response into Trade instances."""
    if not isinstance(body, dict):
        return []
    d = cast(dict[str, Any], body)
    raw = d.get("trades", [])
    if not isinstance(raw, list):
        return []
    items = cast(list[Any], raw)
    return [Trade.model_validate(item) for item in items]


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

    def latest_trade(self, symbol: str, board_id: BoardId) -> list[Trade]:
        """Get latest trade for a symbol.

        Args:
            symbol: Security symbol (e.g. "HPG").
            board_id: Board filter.

        Returns:
            List of Trade instances.
        """
        path = f"/price/{symbol}/trades/latest"
        params = {"boardId": board_id.value}
        headers = self._client._request_headers("GET", path)
        response = self._client._send("GET", path, headers=headers, params=params)
        handle_response(
            response.status_code,
            response.text,
            dict(response.headers),
            trading_token_set=self._client._trading_token is not None,
        )
        return _parse_trade_list(response.json())

    def trades(
        self,
        symbol: str,
        board_id: BoardId,
        from_ts: str,
        to_ts: str,
        limit: int | None = None,
    ) -> list[Trade]:
        """Get trade history for a symbol.

        Args:
            symbol: Security symbol (e.g. "HPG").
            board_id: Board filter.
            from_ts: Start timestamp string.
            to_ts: End timestamp string.
            limit: Optional max number of trades.

        Returns:
            List of Trade instances.
        """
        path = f"/price/{symbol}/trades"
        params: dict[str, str | int] = {
            "boardId": board_id.value,
            "from": from_ts,
            "to": to_ts,
        }
        if limit is not None:
            params["limit"] = limit
        headers = self._client._request_headers("GET", path)
        response = self._client._send("GET", path, headers=headers, params=params)
        handle_response(
            response.status_code,
            response.text,
            dict(response.headers),
            trading_token_set=self._client._trading_token is not None,
        )
        return _parse_trade_list(response.json())


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

    async def latest_trade(self, symbol: str, board_id: BoardId) -> list[Trade]:
        """Get latest trade for a symbol (async).

        Args:
            symbol: Security symbol (e.g. "HPG").
            board_id: Board filter.

        Returns:
            List of Trade instances.
        """
        path = f"/price/{symbol}/trades/latest"
        params = {"boardId": board_id.value}
        headers = self._client._request_headers("GET", path)
        response = await self._client._async_send("GET", path, headers=headers, params=params)
        handle_response(
            response.status_code,
            response.text,
            dict(response.headers),
            trading_token_set=self._client._trading_token is not None,
        )
        return _parse_trade_list(response.json())

    async def trades(
        self,
        symbol: str,
        board_id: BoardId,
        from_ts: str,
        to_ts: str,
        limit: int | None = None,
    ) -> list[Trade]:
        """Get trade history for a symbol (async).

        Args:
            symbol: Security symbol (e.g. "HPG").
            board_id: Board filter.
            from_ts: Start timestamp string.
            to_ts: End timestamp string.
            limit: Optional max number of trades.

        Returns:
            List of Trade instances.
        """
        path = f"/price/{symbol}/trades"
        params: dict[str, str | int] = {
            "boardId": board_id.value,
            "from": from_ts,
            "to": to_ts,
        }
        if limit is not None:
            params["limit"] = limit
        headers = self._client._request_headers("GET", path)
        response = await self._client._async_send("GET", path, headers=headers, params=params)
        handle_response(
            response.status_code,
            response.text,
            dict(response.headers),
            trading_token_set=self._client._trading_token is not None,
        )
        return _parse_trade_list(response.json())
