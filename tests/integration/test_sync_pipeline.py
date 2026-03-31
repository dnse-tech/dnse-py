"""Sync resource pipeline tests: URL, body, query params, and Pydantic parsing via respx."""

import json

import httpx
import respx

from dnse.client import DnseClient
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


class TestSyncRegistrationPipeline:
    def test_send_otp(self):
        with respx.mock:
            route = respx.post(BASE + "/registration/send-email-otp").mock(
                return_value=httpx.Response(200)
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            client.registration.send_otp()
            request = route.calls.last.request

        assert request.method == "POST"
        assert request.url.path == "/registration/send-email-otp"

    def test_verify_otp_returns_and_stores_token(self):
        with respx.mock:
            respx.post(BASE + "/registration/trading-token").mock(
                return_value=httpx.Response(200, json={"tradingToken": "tok"})
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            result = client.registration.verify_otp("123456")

        assert result == "tok"
        assert client._trading_token == "tok"


class TestSyncAccountsPipeline:
    def test_list(self):
        with respx.mock:
            respx.get(BASE + "/accounts").mock(
                return_value=httpx.Response(200, json={"accounts": []})
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            result = client.accounts.list()

        assert isinstance(result, AccountsResponse)

    def test_balances(self):
        with respx.mock:
            respx.get(BASE + f"/accounts/{ACC}/balances").mock(
                return_value=httpx.Response(200, json={"stock": {}})
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            result = client.accounts.balances(ACC)

        assert isinstance(result, AccountBalanceResponse)

    def test_loan_packages(self):
        with respx.mock:
            route = respx.get(BASE + f"/accounts/{ACC}/loan-packages").mock(
                return_value=httpx.Response(200, json={"loanPackages": []})
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            result = client.accounts.loan_packages(ACC, market_type="STOCK", symbol="HPG")
            request = route.calls.last.request

        assert isinstance(result, LoanPackageResponse)
        assert request.url.params["marketType"] == "STOCK"
        assert request.url.params["symbol"] == "HPG"

    def test_ppse_passes_params(self):
        with respx.mock:
            route = respx.get(BASE + f"/accounts/{ACC}/ppse").mock(
                return_value=httpx.Response(200, json={})
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            client.accounts.ppse(
                ACC, symbol="HPG", price="25.5", market_type="STOCK", loan_package_id=2278
            )
            request = route.calls.last.request

        assert request.url.params["symbol"] == "HPG"
        assert request.url.params["price"] == "25.5"
        assert request.url.params["marketType"] == "STOCK"
        assert request.url.params["loanPackageId"] == "2278"


class TestSyncOrdersPipeline:
    def test_place(self):
        with respx.mock:
            route = respx.post(BASE + "/accounts/orders").mock(
                return_value=httpx.Response(201, json={"id": 99})
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            client.set_trading_token("tok")
            req = PlaceOrderRequest(
                account_no=ACC, symbol="HPG", side="NB", order_type="LO", quantity=100, price=25.0
            )
            result = client.orders.place(req, market_type="STOCK", order_category="NORMAL")
            request = route.calls.last.request
            body = json.loads(request.content)

        assert isinstance(result, PlaceOrderResponse)
        assert result.id == 99
        assert body["accountNo"] == ACC
        assert body["symbol"] == "HPG"
        assert body["side"] == "NB"
        assert body["orderType"] == "LO"
        assert body["quantity"] == 100
        assert body["price"] == 25.0
        assert request.url.params["marketType"] == "STOCK"
        assert request.url.params["orderCategory"] == "NORMAL"

    def test_list_passes_params(self):
        with respx.mock:
            route = respx.get(BASE + f"/accounts/{ACC}/orders").mock(
                return_value=httpx.Response(200, json={"orders": []})
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            result = client.orders.list(ACC, market_type="STOCK", order_category="NORMAL")
            request = route.calls.last.request

        assert isinstance(result, GetOrdersResponse)
        assert request.url.params["marketType"] == "STOCK"

    def test_get(self):
        with respx.mock:
            respx.get(BASE + f"/accounts/{ACC}/orders/99").mock(
                return_value=httpx.Response(200, json={"id": 99})
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            result = client.orders.get(ACC, 99, market_type="STOCK", order_category="NORMAL")

        assert isinstance(result, OrderItem)
        assert result.id == 99

    def test_update(self):
        with respx.mock:
            route = respx.put(BASE + f"/accounts/{ACC}/orders/99").mock(
                return_value=httpx.Response(200, json={"id": 99})
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            client.set_trading_token("tok")
            result = client.orders.update(
                ACC,
                99,
                UpdateOrderRequest(price=26.0),
                market_type="STOCK",
                order_category="NORMAL",
            )
            request = route.calls.last.request
            body = json.loads(request.content)

        assert isinstance(result, OrderItem)
        assert body["price"] == 26.0
        assert request.url.params["marketType"] == "STOCK"
        assert request.url.params["orderCategory"] == "NORMAL"

    def test_cancel_returns_none(self):
        with respx.mock:
            respx.delete(BASE + f"/accounts/{ACC}/orders/99").mock(return_value=httpx.Response(204))
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            client.set_trading_token("tok")
            result = client.orders.cancel(ACC, 99, market_type="STOCK", order_category="NORMAL")

        assert result is None

    def test_history_passes_params(self):
        with respx.mock:
            route = respx.get(BASE + f"/accounts/{ACC}/orders/history").mock(
                return_value=httpx.Response(200, json={"data": [], "total": 0})
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            result = client.orders.history(ACC, **{"from": "2024-01-01"})
            request = route.calls.last.request

        assert isinstance(result, OrderHistoryResponse)
        assert request.url.params["from"] == "2024-01-01"


class TestSyncDealsPipeline:
    def test_list(self):
        with respx.mock:
            respx.get(BASE + f"/accounts/{ACC}/positions").mock(
                return_value=httpx.Response(200, json={"deals": []})
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            result = client.deals.list(ACC, market_type="STOCK")

        assert isinstance(result, DealsResponse)


class TestSyncMarketPipeline:
    def test_security_info(self):
        with respx.mock:
            respx.get(BASE + "/price/HPG/secdef").mock(
                return_value=httpx.Response(200, json=[{"symbol": "HPG", "boardId": "AL"}])
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            result = client.market.security_info("HPG")

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], SecurityDefinition)
        assert result[0].symbol == "HPG"

    def test_security_info_with_board_id(self):
        from dnse.models.market import BoardId

        with respx.mock:
            route = respx.get(BASE + "/price/HPG/secdef").mock(
                return_value=httpx.Response(200, json=[{"symbol": "HPG", "boardId": "G1"}])
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            result = client.market.security_info("HPG", board_id=BoardId.ROUND_LOT)

        assert result[0].board_id == "G1"  # raw string from server
        assert "boardId=G1" in str(route.calls.last.request.url)
