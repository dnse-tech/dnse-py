"""Async resource integration tests covering all AsyncXxxResource methods."""

from unittest.mock import AsyncMock, patch

import httpx

from dnse.async_client import AsyncDnseClient
from dnse.models.accounts import (
    AccountBalanceResponse,
    AccountsResponse,
    LoanPackageResponse,
)
from dnse.models.deals import DealsResponse
from dnse.models.market import SecurityDefinition
from dnse.models.orders import (
    GetOrdersResponse,
    OrderHistoryResponse,
    OrderItem,
    PlaceOrderRequest,
    PlaceOrderResponse,
    UpdateOrderRequest,
)

# ---------------------------------------------------------------------------
# Async Accounts
# ---------------------------------------------------------------------------


class TestAsyncAccountsResource:
    async def test_list_calls_endpoint(self):
        mock_response = httpx.Response(200, json={"accounts": []})
        with patch.object(AsyncDnseClient, "_async_send", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                result = await client.accounts.list()
        assert isinstance(result, AccountsResponse)
        call_args = mock_send.call_args
        assert call_args[0][0] == "GET"
        assert call_args[0][1] == "/accounts"

    async def test_balances_calls_endpoint(self):
        mock_response = httpx.Response(200, json={"stock": {}})
        with patch.object(AsyncDnseClient, "_async_send", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                result = await client.accounts.balances("123")
        assert isinstance(result, AccountBalanceResponse)
        call_args = mock_send.call_args
        assert call_args[0][0] == "GET"
        assert "/accounts/123/balances" in call_args[0][1]

    async def test_loan_packages_calls_endpoint(self):
        mock_response = httpx.Response(200, json={"loanPackages": []})
        with patch.object(AsyncDnseClient, "_async_send", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                result = await client.accounts.loan_packages("456")
        assert isinstance(result, LoanPackageResponse)
        call_args = mock_send.call_args
        assert "/accounts/456/loan-packages" in call_args[0][1]

    async def test_ppse_calls_endpoint_with_params(self):
        mock_response = httpx.Response(200, json={"price": 27000.0})
        with patch.object(AsyncDnseClient, "_async_send", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                await client.accounts.ppse("789", symbol="HPG", price="27000")
        call_args = mock_send.call_args
        assert call_args[0][0] == "GET"
        assert "/accounts/789/ppse" in call_args[0][1]
        assert call_args[1]["params"]["symbol"] == "HPG"
        assert call_args[1]["params"]["price"] == "27000"


# ---------------------------------------------------------------------------
# Async Orders
# ---------------------------------------------------------------------------


class TestAsyncOrdersResource:
    def _make_place_req(self) -> PlaceOrderRequest:
        return PlaceOrderRequest(
            account_no="123",
            symbol="HPG",
            side="NB",
            order_type="LO",
            quantity=100,
            price=27000.0,
        )

    async def test_place_calls_endpoint(self):
        mock_response = httpx.Response(201, json={"id": 1})
        with patch.object(AsyncDnseClient, "_async_send", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                client.set_trading_token("tok")
                result = await client.orders.place(self._make_place_req())
        assert isinstance(result, PlaceOrderResponse)
        call_args = mock_send.call_args
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/accounts/orders"

    async def test_list_calls_endpoint(self):
        mock_response = httpx.Response(200, json={"orders": []})
        with patch.object(AsyncDnseClient, "_async_send", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                result = await client.orders.list("123")
        assert isinstance(result, GetOrdersResponse)
        call_args = mock_send.call_args
        assert call_args[0][0] == "GET"
        assert "/accounts/123/orders" in call_args[0][1]

    async def test_get_calls_endpoint(self):
        mock_response = httpx.Response(200, json={"id": 42})
        with patch.object(AsyncDnseClient, "_async_send", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                result = await client.orders.get("123", 42)
        assert isinstance(result, OrderItem)
        call_args = mock_send.call_args
        assert "/accounts/123/orders/42" in call_args[0][1]

    async def test_update_calls_endpoint(self):
        mock_response = httpx.Response(200, json={"id": 42})
        with patch.object(AsyncDnseClient, "_async_send", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                client.set_trading_token("tok")
                req = UpdateOrderRequest(price=27500.0)
                result = await client.orders.update("123", 42, req)
        assert isinstance(result, OrderItem)
        call_args = mock_send.call_args
        assert call_args[0][0] == "PUT"
        assert "/accounts/123/orders/42" in call_args[0][1]

    async def test_cancel_calls_endpoint(self):
        mock_response = httpx.Response(204)
        with patch.object(AsyncDnseClient, "_async_send", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                client.set_trading_token("tok")
                result = await client.orders.cancel("123", 42)
        assert result is None
        call_args = mock_send.call_args
        assert call_args[0][0] == "DELETE"
        assert "/accounts/123/orders/42" in call_args[0][1]

    async def test_history_calls_endpoint(self):
        mock_response = httpx.Response(200, json={"data": []})
        with patch.object(AsyncDnseClient, "_async_send", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                result = await client.orders.history("123", **{"from": "2026-01-01"})
        assert isinstance(result, OrderHistoryResponse)
        call_args = mock_send.call_args
        assert "/accounts/123/orders/history" in call_args[0][1]

    async def test_list_passes_params(self):
        mock_response = httpx.Response(200, json={"orders": []})
        with patch.object(AsyncDnseClient, "_async_send", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                await client.orders.list("123", marketType="STOCK")
        call_args = mock_send.call_args
        assert call_args[1]["params"]["marketType"] == "STOCK"


# ---------------------------------------------------------------------------
# Async Deals
# ---------------------------------------------------------------------------


class TestAsyncDealsResource:
    async def test_list_calls_endpoint(self):
        mock_response = httpx.Response(200, json={"deals": []})
        with patch.object(AsyncDnseClient, "_async_send", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                result = await client.deals.list("123")
        assert isinstance(result, DealsResponse)
        call_args = mock_send.call_args
        assert call_args[0][0] == "GET"
        assert "/accounts/123/deals" in call_args[0][1]

    async def test_list_passes_params(self):
        mock_response = httpx.Response(200, json={"deals": []})
        with patch.object(AsyncDnseClient, "_async_send", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                await client.deals.list("123", marketType="STOCK", pageSize=10)
        call_args = mock_send.call_args
        assert call_args[1]["params"]["marketType"] == "STOCK"
        assert call_args[1]["params"]["pageSize"] == 10


# ---------------------------------------------------------------------------
# Async Market
# ---------------------------------------------------------------------------


class TestAsyncMarketResource:
    async def test_security_info_calls_endpoint(self):
        mock_response = httpx.Response(200, json=[{"symbol": "HPG"}])
        with patch.object(AsyncDnseClient, "_async_send", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                result = await client.market.security_info("HPG")
        assert isinstance(result, list)
        assert isinstance(result[0], SecurityDefinition)
        call_args = mock_send.call_args
        assert call_args[0][0] == "GET"
        assert "/price/secdef/HPG" in call_args[0][1]


# ---------------------------------------------------------------------------
# Async Registration
# ---------------------------------------------------------------------------


class TestAsyncRegistrationResource:
    async def test_verify_otp_returns_token_and_sets_it(self):
        mock_response = httpx.Response(200, json={"tradingToken": "tok999"})
        with patch.object(AsyncDnseClient, "_async_send", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                token = await client.registration.verify_otp("123456")
        assert token == "tok999"

    async def test_verify_otp_custom_type(self):
        mock_response = httpx.Response(200, json={"tradingToken": "tok"})
        with patch.object(AsyncDnseClient, "_async_send", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            async with AsyncDnseClient(api_key="key", api_secret="secret") as client:
                await client.registration.verify_otp("000000", otp_type="sms_otp")
        # Verify correct path used
        call_args = mock_send.call_args
        assert "/registration/trading-token" in call_args[0][1]
