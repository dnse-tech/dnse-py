"""Async resource pipeline tests: full-pipeline verification via respx and AsyncDnseClient."""

import json

import httpx
import respx

from dnse.async_client import AsyncDnseClient
from dnse.models.accounts import AccountBalanceResponse, AccountsResponse, LoanPackageResponse
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

from tests.integration.conftest import BASE_URL, FAKE_ACCOUNT, FAKE_KEY, FAKE_SECRET

BASE = BASE_URL
ACC = FAKE_ACCOUNT


class TestAsyncAuthPipeline:
    async def test_hmac_headers_on_async_request(self):
        with respx.mock:
            route = respx.get(BASE + "/accounts").mock(
                return_value=httpx.Response(200, json={"accounts": []})
            )
            async with AsyncDnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET) as client:
                await client.accounts.list()
            request = route.calls.last.request

        assert request.headers["x-api-key"] == FAKE_KEY
        assert "date" in request.headers
        assert request.headers["x-signature"].startswith('Signature keyId="testkey"')
        assert "nonce" in request.headers

    async def test_trading_token_on_async_order_mutation(self):
        with respx.mock:
            route = respx.post(BASE + "/accounts/orders").mock(
                return_value=httpx.Response(201, json={"id": 1})
            )
            async with AsyncDnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET) as client:
                client.set_trading_token("tok123")
                req = PlaceOrderRequest(
                    account_no=ACC, symbol="HPG", side="NB", order_type="LO", quantity=100, price=25.0
                )
                await client.orders.place(req)
            request = route.calls.last.request

        assert request.headers["trading-token"] == "tok123"


class TestAsyncRegistrationPipeline:
    async def test_verify_otp_sets_token(self):
        with respx.mock:
            respx.post(BASE + "/registration/trading-token").mock(
                return_value=httpx.Response(200, json={"tradingToken": "tok"})
            )
            async with AsyncDnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET) as client:
                result = await client.registration.verify_otp("123456")
                token_stored = client._trading_token

        assert result == "tok"
        assert token_stored == "tok"


class TestAsyncAccountsPipeline:
    async def test_list(self):
        with respx.mock:
            respx.get(BASE + "/accounts").mock(
                return_value=httpx.Response(200, json={"accounts": []})
            )
            async with AsyncDnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET) as client:
                result = await client.accounts.list()

        assert isinstance(result, AccountsResponse)

    async def test_balances(self):
        with respx.mock:
            respx.get(BASE + f"/accounts/{ACC}/balances").mock(
                return_value=httpx.Response(200, json={"stock": {}})
            )
            async with AsyncDnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET) as client:
                result = await client.accounts.balances(ACC)

        assert isinstance(result, AccountBalanceResponse)

    async def test_loan_packages(self):
        with respx.mock:
            respx.get(BASE + f"/accounts/{ACC}/loan-packages").mock(
                return_value=httpx.Response(200, json={"loanPackages": []})
            )
            async with AsyncDnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET) as client:
                result = await client.accounts.loan_packages(ACC)

        assert isinstance(result, LoanPackageResponse)

    async def test_ppse_params(self):
        with respx.mock:
            route = respx.get(BASE + f"/accounts/{ACC}/ppse").mock(
                return_value=httpx.Response(200, json={})
            )
            async with AsyncDnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET) as client:
                await client.accounts.ppse(ACC, symbol="HPG", price="25.5")
            request = route.calls.last.request

        assert request.url.params["symbol"] == "HPG"
        assert request.url.params["price"] == "25.5"


class TestAsyncOrdersPipeline:
    async def test_place(self):
        with respx.mock:
            route = respx.post(BASE + "/accounts/orders").mock(
                return_value=httpx.Response(201, json={"id": 99})
            )
            async with AsyncDnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET) as client:
                client.set_trading_token("tok")
                req = PlaceOrderRequest(
                    account_no=ACC, symbol="HPG", side="NB", order_type="LO", quantity=100, price=25.0
                )
                result = await client.orders.place(req)
            body = json.loads(route.calls.last.request.content)

        assert isinstance(result, PlaceOrderResponse)
        assert result.id == 99
        assert body["accountNo"] == ACC
        assert body["symbol"] == "HPG"

    async def test_list_with_params(self):
        with respx.mock:
            route = respx.get(BASE + f"/accounts/{ACC}/orders").mock(
                return_value=httpx.Response(200, json={"orders": []})
            )
            async with AsyncDnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET) as client:
                result = await client.orders.list(ACC, marketType="STOCK")
            request = route.calls.last.request

        assert isinstance(result, GetOrdersResponse)
        assert request.url.params["marketType"] == "STOCK"

    async def test_get(self):
        with respx.mock:
            respx.get(BASE + f"/accounts/{ACC}/orders/99").mock(
                return_value=httpx.Response(200, json={"id": 99})
            )
            async with AsyncDnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET) as client:
                result = await client.orders.get(ACC, 99)

        assert isinstance(result, OrderItem)
        assert result.id == 99

    async def test_update(self):
        with respx.mock:
            route = respx.put(BASE + f"/accounts/{ACC}/orders/99").mock(
                return_value=httpx.Response(200, json={"id": 99})
            )
            async with AsyncDnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET) as client:
                client.set_trading_token("tok")
                result = await client.orders.update(ACC, 99, UpdateOrderRequest(price=26.0))
            body = json.loads(route.calls.last.request.content)

        assert isinstance(result, OrderItem)
        assert body["price"] == 26.0

    async def test_cancel(self):
        with respx.mock:
            respx.delete(BASE + f"/accounts/{ACC}/orders/99").mock(
                return_value=httpx.Response(204)
            )
            async with AsyncDnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET) as client:
                client.set_trading_token("tok")
                result = await client.orders.cancel(ACC, 99)

        assert result is None

    async def test_history(self):
        with respx.mock:
            route = respx.get(BASE + f"/accounts/{ACC}/orders/history").mock(
                return_value=httpx.Response(200, json={"data": [], "total": 0})
            )
            async with AsyncDnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET) as client:
                result = await client.orders.history(ACC, **{"from": "2024-01-01"})
            request = route.calls.last.request

        assert isinstance(result, OrderHistoryResponse)
        assert request.url.params["from"] == "2024-01-01"


class TestAsyncDealsPipeline:
    async def test_list(self):
        with respx.mock:
            respx.get(BASE + f"/accounts/{ACC}/deals").mock(
                return_value=httpx.Response(200, json={"deals": []})
            )
            async with AsyncDnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET) as client:
                result = await client.deals.list(ACC)

        assert isinstance(result, DealsResponse)


class TestAsyncMarketPipeline:
    async def test_security_info(self):
        with respx.mock:
            respx.get(BASE + "/price/secdef/HPG").mock(
                return_value=httpx.Response(200, json={"symbol": "HPG"})
            )
            async with AsyncDnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET) as client:
                result = await client.market.security_info("HPG")

        assert isinstance(result, SecurityDefinition)
        assert result.symbol == "HPG"
