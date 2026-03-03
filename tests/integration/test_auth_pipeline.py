"""Full-pipeline auth tests: verify HMAC headers and trading-token logic via respx transport."""

import httpx
import respx

from dnse.client import DnseClient
from dnse.models.orders import PlaceOrderRequest

from tests.integration.conftest import BASE_URL, FAKE_ACCOUNT, FAKE_KEY, FAKE_SECRET

BASE = BASE_URL


class TestHmacHeadersPresence:
    def test_hmac_headers_present_on_every_request(self):
        with respx.mock:
            route = respx.get(BASE + "/accounts").mock(
                return_value=httpx.Response(200, json={"accounts": []})
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            client.accounts.list()
            request = route.calls.last.request

        assert request.headers["x-api-key"] == FAKE_KEY
        assert "date" in request.headers
        assert request.headers["x-signature"].startswith('Signature keyId="testkey"')
        assert "nonce" in request.headers

    def test_date_header_variant_x_aux_date(self):
        with respx.mock:
            route = respx.get(BASE + "/accounts").mock(
                return_value=httpx.Response(200, json={"accounts": []})
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET, date_header="x-aux-date")
            client.accounts.list()
            request = route.calls.last.request

        assert "x-aux-date" in request.headers
        assert "date" not in request.headers
        assert "x-aux-date" in request.headers["x-signature"]


class TestTradingTokenInjection:
    def test_trading_token_injected_on_place_order(self):
        with respx.mock:
            route = respx.post(BASE + "/accounts/orders").mock(
                return_value=httpx.Response(201, json={"id": 1})
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            client.set_trading_token("tok123")
            order_req = PlaceOrderRequest(
                account_no=FAKE_ACCOUNT,
                symbol="HPG",
                side="NB",
                order_type="LO",
                quantity=100,
                price=25.0,
            )
            client.orders.place(order_req)
            request = route.calls.last.request

        assert request.headers["trading-token"] == "tok123"

    def test_trading_token_not_injected_on_get_orders(self):
        with respx.mock:
            route = respx.get(BASE + f"/accounts/{FAKE_ACCOUNT}/orders").mock(
                return_value=httpx.Response(200, json={"orders": []})
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            client.set_trading_token("tok123")
            client.orders.list(FAKE_ACCOUNT)
            request = route.calls.last.request

        assert "trading-token" not in request.headers

    def test_trading_token_not_injected_on_non_order_post(self):
        with respx.mock:
            route = respx.post(BASE + "/registration/send-email-otp").mock(
                return_value=httpx.Response(200)
            )
            client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
            client.set_trading_token("tok123")
            client.registration.send_otp()
            request = route.calls.last.request

        assert "trading-token" not in request.headers


class TestNoCredentials:
    def test_no_auth_headers_without_credentials(self):
        with respx.mock:
            route = respx.get(BASE + "/accounts").mock(
                return_value=httpx.Response(200, json={"accounts": []})
            )
            client = DnseClient(api_key="", api_secret="")
            client.accounts.list()
            request = route.calls.last.request

        assert "x-api-key" not in request.headers
        assert "x-signature" not in request.headers
