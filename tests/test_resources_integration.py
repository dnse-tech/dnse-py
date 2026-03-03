"""Integration tests for resources using mocked httpx responses."""

from unittest.mock import AsyncMock, patch

import httpx

from dnse.async_client import AsyncDnseClient
from dnse.client import DnseClient
from dnse.models.accounts import AccountsResponse
from dnse.models.orders import PlaceOrderRequest, PlaceOrderResponse


class TestRegistrationResourceMocked:
    """Test registration resource with mocked HTTP."""

    def test_send_otp_calls_endpoint(self):
        """send_otp calls POST /registration/send-email-otp."""
        with patch.object(DnseClient, '_send') as mock_send:
            mock_send.return_value = httpx.Response(200)
            with DnseClient(api_key="key", api_secret="secret") as client:
                client.registration.send_otp()
            # Verify _send was called with correct path
            assert mock_send.called
            call_args = mock_send.call_args
            assert call_args[0][1] == "/registration/send-email-otp"  # path argument
            assert call_args[0][0] == "POST"  # method argument

    def test_verify_otp_returns_token(self):
        """verify_otp parses token from response."""
        mock_response = httpx.Response(200, json={"tradingToken": "token123"})
        with patch.object(DnseClient, '_send') as mock_send:
            mock_send.return_value = mock_response
            with DnseClient(api_key="key", api_secret="secret") as client:
                token = client.registration.verify_otp("123456")
            assert token == "token123"
            assert client._trading_token == "token123"


class TestAccountsResourceMocked:
    """Test accounts resource with mocked HTTP."""

    def test_list_calls_endpoint(self):
        """accounts.list calls GET /accounts."""
        mock_response = httpx.Response(200, json={"accounts": []})
        with patch.object(DnseClient, '_send') as mock_send:
            mock_send.return_value = mock_response
            with DnseClient(api_key="key", api_secret="secret") as client:
                result = client.accounts.list()
            assert isinstance(result, AccountsResponse)
            call_args = mock_send.call_args
            assert call_args[0][0] == "GET"
            assert call_args[0][1] == "/accounts"

    def test_balances_calls_endpoint(self):
        """accounts.balances calls GET /accounts/{id}/balances."""
        mock_response = httpx.Response(200, json={"stock": {}})
        with patch.object(DnseClient, '_send') as mock_send:
            mock_send.return_value = mock_response
            with DnseClient(api_key="key", api_secret="secret") as client:
                result = client.accounts.balances("123")
            call_args = mock_send.call_args
            assert "/accounts/123/balances" in call_args[0][1]

    def test_loan_packages_calls_endpoint(self):
        """accounts.loan_packages calls GET /accounts/{id}/loan-packages."""
        mock_response = httpx.Response(200, json={"loanPackages": []})
        with patch.object(DnseClient, '_send') as mock_send:
            mock_send.return_value = mock_response
            with DnseClient(api_key="key", api_secret="secret") as client:
                result = client.accounts.loan_packages("456")
            call_args = mock_send.call_args
            assert "/accounts/456/loan-packages" in call_args[0][1]

    def test_ppse_calls_endpoint(self):
        """accounts.ppse calls GET /accounts/{id}/ppse with params."""
        mock_response = httpx.Response(200, json={"price": 27000.0})
        with patch.object(DnseClient, '_send') as mock_send:
            mock_send.return_value = mock_response
            with DnseClient(api_key="key", api_secret="secret") as client:
                result = client.accounts.ppse("789", symbol="HPG", price="27000")
            call_args = mock_send.call_args
            assert "/accounts/789/ppse" in call_args[0][1]
            # params should be in kwargs
            assert "params" in call_args[1]
            assert call_args[1]["params"]["symbol"] == "HPG"


class TestOrdersResourceMocked:
    """Test orders resource with mocked HTTP."""

    def test_place_order_calls_endpoint(self):
        """orders.place calls POST /accounts/orders."""
        mock_response = httpx.Response(201, json={"id": 1})
        with patch.object(DnseClient, '_send') as mock_send:
            mock_send.return_value = mock_response
            with DnseClient(api_key="key", api_secret="secret") as client:
                client.set_trading_token("token")
                req = PlaceOrderRequest(
                    account_no="123",
                    symbol="HPG",
                    side="NB",
                    order_type="LO",
                    quantity=100,
                    price=27000.0,
                )
                result = client.orders.place(req)
            assert isinstance(result, PlaceOrderResponse)
            call_args = mock_send.call_args
            assert call_args[0][0] == "POST"
            assert call_args[0][1] == "/accounts/orders"

    def test_list_calls_endpoint(self):
        """orders.list calls GET /accounts/{id}/orders."""
        mock_response = httpx.Response(200, json={"orders": []})
        with patch.object(DnseClient, '_send') as mock_send:
            mock_send.return_value = mock_response
            with DnseClient(api_key="key", api_secret="secret") as client:
                result = client.orders.list("123")
            call_args = mock_send.call_args
            assert call_args[0][0] == "GET"
            assert "/accounts/123/orders" in call_args[0][1]

    def test_get_calls_endpoint(self):
        """orders.get calls GET /accounts/{id}/orders/{order_id}."""
        mock_response = httpx.Response(200, json={"id": 42})
        with patch.object(DnseClient, '_send') as mock_send:
            mock_send.return_value = mock_response
            with DnseClient(api_key="key", api_secret="secret") as client:
                result = client.orders.get("123", 42)
            call_args = mock_send.call_args
            assert "/accounts/123/orders/42" in call_args[0][1]

    def test_update_calls_endpoint(self):
        """orders.update calls PUT /accounts/{id}/orders/{order_id}."""
        mock_response = httpx.Response(200, json={"id": 42})
        with patch.object(DnseClient, '_send') as mock_send:
            mock_send.return_value = mock_response
            with DnseClient(api_key="key", api_secret="secret") as client:
                client.set_trading_token("token")
                from dnse.models.orders import UpdateOrderRequest
                req = UpdateOrderRequest(price=27500.0)
                result = client.orders.update("123", 42, req)
            call_args = mock_send.call_args
            assert call_args[0][0] == "PUT"
            assert "/accounts/123/orders/42" in call_args[0][1]

    def test_cancel_calls_endpoint(self):
        """orders.cancel calls DELETE /accounts/{id}/orders/{order_id}."""
        mock_response = httpx.Response(204)
        with patch.object(DnseClient, '_send') as mock_send:
            mock_send.return_value = mock_response
            with DnseClient(api_key="key", api_secret="secret") as client:
                client.set_trading_token("token")
                result = client.orders.cancel("123", 42)
            assert result is None
            call_args = mock_send.call_args
            assert call_args[0][0] == "DELETE"

    def test_history_calls_endpoint(self):
        """orders.history calls GET /accounts/{id}/orders/history."""
        mock_response = httpx.Response(200, json={"data": []})
        with patch.object(DnseClient, '_send') as mock_send:
            mock_send.return_value = mock_response
            with DnseClient(api_key="key", api_secret="secret") as client:
                result = client.orders.history("123", **{"from": "2026-01-01"})
            call_args = mock_send.call_args
            assert "/accounts/123/orders/history" in call_args[0][1]


class TestDealsResourceMocked:
    """Test deals resource with mocked HTTP."""

    def test_list_calls_endpoint(self):
        """deals.list calls GET /accounts/{id}/deals."""
        mock_response = httpx.Response(200, json={"deals": []})
        with patch.object(DnseClient, '_send') as mock_send:
            mock_send.return_value = mock_response
            with DnseClient(api_key="key", api_secret="secret") as client:
                result = client.deals.list("123")
            call_args = mock_send.call_args
            assert call_args[0][0] == "GET"
            assert "/accounts/123/deals" in call_args[0][1]


class TestMarketResourceMocked:
    """Test market resource with mocked HTTP."""

    def test_security_info_calls_endpoint(self):
        """market.security_info calls GET /price/secdef/{symbol}."""
        mock_response = httpx.Response(200, json={"symbol": "HPG"})
        with patch.object(DnseClient, '_send') as mock_send:
            mock_send.return_value = mock_response
            with DnseClient(api_key="key", api_secret="secret") as client:
                result = client.market.security_info("HPG")
            call_args = mock_send.call_args
            assert call_args[0][0] == "GET"
            assert "/price/secdef/HPG" in call_args[0][1]


class TestAsyncResourcesMocked:
    """Test async resources with mocked HTTP."""

    async def test_async_registration_send_otp(self):
        """Async registration.send_otp calls correct endpoint."""
        mock_response = httpx.Response(200)
        with patch.object(AsyncDnseClient, '_async_send', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                await client.registration.send_otp()
            assert mock_send.called
            call_args = mock_send.call_args
            assert call_args[0][0] == "POST"

    async def test_async_accounts_list(self):
        """Async accounts.list calls correct endpoint."""
        mock_response = httpx.Response(200, json={"accounts": []})
        with patch.object(AsyncDnseClient, '_async_send', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                result = await client.accounts.list()
            call_args = mock_send.call_args
            assert call_args[0][0] == "GET"
            assert call_args[0][1] == "/accounts"

    async def test_async_orders_place(self):
        """Async orders.place calls correct endpoint."""
        mock_response = httpx.Response(201, json={"id": 1})
        with patch.object(AsyncDnseClient, '_async_send', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                client.set_trading_token("token")
                req = PlaceOrderRequest(
                    account_no="123",
                    symbol="HPG",
                    side="NB",
                    order_type="LO",
                    quantity=100,
                    price=27000.0,
                )
                result = await client.orders.place(req)
            call_args = mock_send.call_args
            assert call_args[0][0] == "POST"
