"""Orders resource: full CRUD for stock orders (trading-token required on mutations)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dnse._http import handle_response
from dnse.models.orders import (
    GetOrdersResponse,
    OrderHistoryResponse,
    OrderItem,
    PlaceOrderRequest,
    PlaceOrderResponse,
    UpdateOrderRequest,
)

if TYPE_CHECKING:
    from dnse._base_client import BaseClient
    from dnse.async_client import AsyncDnseClient


class OrdersResource:
    """Sync resource for order endpoints."""

    def __init__(self, client: BaseClient) -> None:
        """Initialize with a sync client reference."""
        self._client = client

    def place(
        self, request: PlaceOrderRequest, *, market_type: str, order_category: str
    ) -> PlaceOrderResponse:
        """Place a new order.

        Requires an active trading token on the client.
        Sends POST /accounts/orders with camelCase JSON body and required query params.

        Args:
            request: Order parameters (body fields).
            market_type: Market type query param (e.g. "STOCK").
            order_category: Order category query param (e.g. "NORMAL").

        Returns:
            PlaceOrderResponse with order ID and status.
        """
        path = "/accounts/orders"
        headers = self._client._request_headers("POST", path)
        params = {"marketType": market_type, "orderCategory": order_category}
        response = self._client._send(
            "POST", path, headers=headers, json=request.model_dump(by_alias=True), params=params
        )
        return self._client._parse(response, PlaceOrderResponse)

    def list(
        self, account_no: str, *, market_type: str, order_category: str, **params: Any
    ) -> GetOrdersResponse:
        """Get the current order book for a sub-account.

        Args:
            account_no: Sub-account number.
            market_type: Market type query param (e.g. "STOCK").
            order_category: Order category query param (e.g. "NORMAL").
            **params: Additional query params.

        Returns:
            GetOrdersResponse with list of active orders.
        """
        path = f"/accounts/{account_no}/orders"
        headers = self._client._request_headers("GET", path)
        query = {"marketType": market_type, "orderCategory": order_category, **params}
        response = self._client._send("GET", path, headers=headers, params=query)
        return self._client._parse(response, GetOrdersResponse)

    def get(
        self, account_no: str, order_id: int, *, market_type: str, order_category: str
    ) -> OrderItem:
        """Get details of a single order.

        Args:
            account_no: Sub-account number.
            order_id: Order ID.
            market_type: Market type query param (e.g. "STOCK").
            order_category: Order category query param (e.g. "NORMAL").

        Returns:
            OrderItem with full order details.
        """
        path = f"/accounts/{account_no}/orders/{order_id}"
        headers = self._client._request_headers("GET", path)
        params = {"marketType": market_type, "orderCategory": order_category}
        response = self._client._send("GET", path, headers=headers, params=params)
        return self._client._parse(response, OrderItem)

    def update(
        self,
        account_no: str,
        order_id: int,
        request: UpdateOrderRequest,
        *,
        market_type: str,
        order_category: str,
    ) -> OrderItem:
        """Modify an existing order (quantity and/or price).

        Requires an active trading token. Sends only non-None fields.

        .. warning::
            DNSE implements modification as cancel-then-replace: the original order
            is cancelled and a **new** order is created with a new ID. The returned
            ``OrderItem.id`` will differ from ``order_id``. Any code that needs to
            track or cancel the order after calling ``update()`` must use the new ID
            from the returned object, not the original ``order_id``.

        Args:
            account_no: Sub-account number.
            order_id: Order ID to modify.
            request: Fields to update (None fields excluded).
            market_type: Market type query param (e.g. "STOCK").
            order_category: Order category query param (e.g. "NORMAL").

        Returns:
            OrderItem for the newly created replacement order (new ID).
        """
        path = f"/accounts/{account_no}/orders/{order_id}"
        headers = self._client._request_headers("PUT", path)
        params = {"marketType": market_type, "orderCategory": order_category}
        response = self._client._send(
            "PUT",
            path,
            headers=headers,
            json=request.model_dump(by_alias=True, exclude_none=True),
            params=params,
        )
        return self._client._parse(response, OrderItem)

    def cancel(
        self, account_no: str, order_id: int, *, market_type: str, order_category: str
    ) -> None:
        """Cancel an order.

        Requires an active trading token. Expects 204 No Content.

        Args:
            account_no: Sub-account number.
            order_id: Order ID to cancel.
            market_type: Market type query param (e.g. "STOCK").
            order_category: Order category query param (e.g. "NORMAL").
        """
        path = f"/accounts/{account_no}/orders/{order_id}"
        headers = self._client._request_headers("DELETE", path)
        params = {"marketType": market_type, "orderCategory": order_category}
        response = self._client._send("DELETE", path, headers=headers, params=params)
        handle_response(
            response.status_code,
            response.text,
            dict(response.headers),
            trading_token_set=self._client._trading_token is not None,
        )

    def history(self, account_no: str, **params: Any) -> OrderHistoryResponse:
        """Get historical orders for a sub-account.

        Args:
            account_no: Sub-account number.
            **params: Required query params: from, to (yyyy-mm-dd), marketType, orderCategory.

        Returns:
            OrderHistoryResponse with paginated historical orders.
        """
        path = f"/accounts/{account_no}/orders/history"
        headers = self._client._request_headers("GET", path)
        response = self._client._send("GET", path, headers=headers, params=params or None)
        return self._client._parse(response, OrderHistoryResponse)


class AsyncOrdersResource:
    """Async resource for order endpoints."""

    def __init__(self, client: AsyncDnseClient) -> None:
        """Initialize with an async client reference."""
        self._client = client

    async def place(
        self, request: PlaceOrderRequest, *, market_type: str, order_category: str
    ) -> PlaceOrderResponse:
        """Place a new order (async).

        Args:
            request: Order parameters (body fields).
            market_type: Market type query param (e.g. "STOCK").
            order_category: Order category query param (e.g. "NORMAL").

        Returns:
            PlaceOrderResponse with order ID and status.
        """
        path = "/accounts/orders"
        headers = self._client._request_headers("POST", path)
        params = {"marketType": market_type, "orderCategory": order_category}
        response = await self._client._async_send(
            "POST", path, headers=headers, json=request.model_dump(by_alias=True), params=params
        )
        return self._client._parse(response, PlaceOrderResponse)

    async def list(
        self, account_no: str, *, market_type: str, order_category: str, **params: Any
    ) -> GetOrdersResponse:
        """Get the current order book (async).

        Args:
            account_no: Sub-account number.
            market_type: Market type query param (e.g. "STOCK").
            order_category: Order category query param (e.g. "NORMAL").
            **params: Additional query params.

        Returns:
            GetOrdersResponse with active orders.
        """
        path = f"/accounts/{account_no}/orders"
        headers = self._client._request_headers("GET", path)
        query = {"marketType": market_type, "orderCategory": order_category, **params}
        response = await self._client._async_send("GET", path, headers=headers, params=query)
        return self._client._parse(response, GetOrdersResponse)

    async def get(
        self, account_no: str, order_id: int, *, market_type: str, order_category: str
    ) -> OrderItem:
        """Get a single order (async).

        Args:
            account_no: Sub-account number.
            order_id: Order ID.
            market_type: Market type query param (e.g. "STOCK").
            order_category: Order category query param (e.g. "NORMAL").

        Returns:
            OrderItem.
        """
        path = f"/accounts/{account_no}/orders/{order_id}"
        headers = self._client._request_headers("GET", path)
        params = {"marketType": market_type, "orderCategory": order_category}
        response = await self._client._async_send("GET", path, headers=headers, params=params)
        return self._client._parse(response, OrderItem)

    async def update(
        self,
        account_no: str,
        order_id: int,
        request: UpdateOrderRequest,
        *,
        market_type: str,
        order_category: str,
    ) -> OrderItem:
        """Modify an existing order (async).

        DNSE implements modification as cancel-then-replace: the original order is
        cancelled and a new order is created with a new ID. Use ``returned.id`` for
        any subsequent get/cancel calls — ``order_id`` is no longer valid after this.

        Args:
            account_no: Sub-account number.
            order_id: Order ID to modify.
            request: Fields to update.
            market_type: Market type query param (e.g. "STOCK").
            order_category: Order category query param (e.g. "NORMAL").

        Returns:
            OrderItem for the newly created replacement order (new ID).
        """
        path = f"/accounts/{account_no}/orders/{order_id}"
        headers = self._client._request_headers("PUT", path)
        params = {"marketType": market_type, "orderCategory": order_category}
        response = await self._client._async_send(
            "PUT",
            path,
            headers=headers,
            json=request.model_dump(by_alias=True, exclude_none=True),
            params=params,
        )
        return self._client._parse(response, OrderItem)

    async def cancel(
        self, account_no: str, order_id: int, *, market_type: str, order_category: str
    ) -> None:
        """Cancel an order (async).

        Args:
            account_no: Sub-account number.
            order_id: Order ID.
            market_type: Market type query param (e.g. "STOCK").
            order_category: Order category query param (e.g. "NORMAL").
        """
        path = f"/accounts/{account_no}/orders/{order_id}"
        headers = self._client._request_headers("DELETE", path)
        params = {"marketType": market_type, "orderCategory": order_category}
        response = await self._client._async_send("DELETE", path, headers=headers, params=params)
        handle_response(
            response.status_code,
            response.text,
            dict(response.headers),
            trading_token_set=self._client._trading_token is not None,
        )

    async def history(self, account_no: str, **params: Any) -> OrderHistoryResponse:
        """Get historical orders (async).

        Args:
            account_no: Sub-account number.
            **params: Required query params: from, to, marketType, orderCategory.

        Returns:
            OrderHistoryResponse with paginated historical orders.
        """
        path = f"/accounts/{account_no}/orders/history"
        headers = self._client._request_headers("GET", path)
        response = await self._client._async_send(
            "GET", path, headers=headers, params=params or None
        )
        return self._client._parse(response, OrderHistoryResponse)
