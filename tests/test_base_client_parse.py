"""Tests for BaseClient._parse and session expiry detection."""

import httpx
import pytest
import respx

from dnse.client import DnseClient
from dnse.exceptions import DnseAuthError, DnseSessionExpiredError
from dnse.models.auth import TwoFAResponse

BASE_URL = "https://openapi.dnse.com.vn"


def test_parse_200_with_valid_json():
    """_parse with 200 returns parsed Pydantic model."""
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/test").mock(return_value=httpx.Response(200, json={"tradingToken": "abc123"}))
        with DnseClient() as client:
            response = client.get("/test")
            result = client._parse(response, TwoFAResponse)
        assert isinstance(result, TwoFAResponse)
        assert result.trading_token == "abc123"


def test_parse_401_raises_auth_error():
    """_parse with 401 raises DnseAuthError when parsing."""
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/test").mock(return_value=httpx.Response(401, text="Unauthorized"))
        with DnseClient() as client:
            with pytest.raises(DnseAuthError):
                client.get("/test")


def test_parse_session_expired_with_token():
    """_parse with 401 + INVALID_TRADING_TOKEN + trading_token_set raises DnseSessionExpiredError."""
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/test").mock(
            return_value=httpx.Response(
                401,
                text='{"code": "INVALID_TRADING_TOKEN", "message": "Token expired"}',
                headers={"content-type": "application/json"},
            )
        )
        with DnseClient(api_key="key", api_secret="secret") as client:
            client.set_trading_token("expired-token")
            with pytest.raises(DnseSessionExpiredError) as exc_info:
                client.get("/test")
        assert exc_info.value.status_code == 401


def test_parse_401_without_trading_token_not_session_expired():
    """_parse with 401 + INVALID_TRADING_TOKEN but no trading token raises DnseAuthError."""
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/test").mock(
            return_value=httpx.Response(
                401,
                text='{"code": "INVALID_TRADING_TOKEN"}',
                headers={"content-type": "application/json"},
            )
        )
        with DnseClient() as client:
            with pytest.raises(DnseAuthError) as exc_info:
                client.get("/test")
            # Should be DnseAuthError, not DnseSessionExpiredError
            assert type(exc_info.value) is not DnseSessionExpiredError
            assert isinstance(exc_info.value, DnseAuthError)


def test_trading_token_injection_on_post_orders():
    """_request_headers includes trading-token header for POST /accounts/orders."""
    with respx.mock(base_url=BASE_URL) as mock:
        mock.post("/accounts/orders").mock(return_value=httpx.Response(200, json={"id": 1}))
        with DnseClient(api_key="key", api_secret="secret") as client:
            client.set_trading_token("mytoken123")
            # Make a request to /accounts/orders
            response = client.post("/accounts/orders", json={"symbol": "HPG"})

        # Check that the request included the trading-token header
        request = mock.calls[-1].request
        assert "trading-token" in request.headers
        assert request.headers["trading-token"] == "mytoken123"


def test_trading_token_injection_on_put_orders():
    """_request_headers includes trading-token header for PUT /accounts/orders."""
    with respx.mock(base_url=BASE_URL) as mock:
        mock.put("/accounts/123/orders/456").mock(
            return_value=httpx.Response(200, json={"id": 456})
        )
        with DnseClient(api_key="key", api_secret="secret") as client:
            client.set_trading_token("mytoken456")
            response = client.put("/accounts/123/orders/456", json={"price": 27000})
        # Verify request was made to correct path
        assert len(mock.calls) == 1
        assert "/accounts/123/orders/456" in str(mock.calls[0].request.url)


def test_trading_token_injection_on_delete_orders():
    """_request_headers includes trading-token header for DELETE /accounts/orders."""
    with respx.mock(base_url=BASE_URL) as mock:
        mock.delete("/accounts/123/orders/456").mock(return_value=httpx.Response(204))
        with DnseClient(api_key="key", api_secret="secret") as client:
            client.set_trading_token("mytoken789")
            response = client.delete("/accounts/123/orders/456")
        # Verify request was made to correct path
        assert len(mock.calls) == 1
        assert "/accounts/123/orders/456" in str(mock.calls[0].request.url)


def test_no_trading_token_injection_on_get_orders():
    """_request_headers does NOT include trading-token header for GET /accounts/orders."""
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/accounts/123/orders").mock(return_value=httpx.Response(200, json={"orders": []}))
        with DnseClient(api_key="key", api_secret="secret") as client:
            client.set_trading_token("mytoken")
            response = client.get("/accounts/123/orders")

        request = mock.calls[-1].request
        assert "trading-token" not in request.headers


def test_no_trading_token_injection_on_post_non_orders():
    """_request_headers does NOT include trading-token header for POST on non-orders path."""
    with respx.mock(base_url=BASE_URL) as mock:
        mock.post("/registration/trading-token").mock(
            return_value=httpx.Response(200, json={"tradingToken": "abc"})
        )
        with DnseClient(api_key="key", api_secret="secret") as client:
            client.set_trading_token("already-have-token")
            response = client.post("/registration/trading-token", json={"otp": "123456"})

        request = mock.calls[-1].request
        # Should not have trading-token header because path doesn't contain /accounts/orders
        assert "trading-token" not in request.headers


def test_no_trading_token_injection_when_token_not_set():
    """_request_headers does NOT include trading-token header when token is not set."""
    with respx.mock(base_url=BASE_URL) as mock:
        mock.post("/accounts/orders").mock(return_value=httpx.Response(200, json={"id": 1}))
        with DnseClient(api_key="key", api_secret="secret") as client:
            # Don't set trading token
            response = client.post("/accounts/orders", json={"symbol": "HPG"})

        request = mock.calls[-1].request
        assert "trading-token" not in request.headers


def test_trading_token_injection_complex_path():
    """_request_headers checks /accounts/orders substring match."""
    with respx.mock(base_url=BASE_URL) as mock:
        mock.post("/accounts/orders/complex/path").mock(
            return_value=httpx.Response(200, json={"id": 1})
        )
        with DnseClient(api_key="key", api_secret="secret") as client:
            client.set_trading_token("token")
            response = client.post("/accounts/orders/complex/path", json={})

        request = mock.calls[-1].request
        assert "trading-token" in request.headers


def test_parse_with_error_code_field():
    """handle_response checks both 'code' and 'errorCode' fields."""
    with respx.mock(base_url=BASE_URL) as mock:
        # Test with 'errorCode' instead of 'code'
        mock.get("/test").mock(
            return_value=httpx.Response(
                401,
                text='{"errorCode": "INVALID_TRADING_TOKEN", "message": "Token expired"}',
                headers={"content-type": "application/json"},
            )
        )
        with DnseClient(api_key="key", api_secret="secret") as client:
            client.set_trading_token("expired-token")
            with pytest.raises(DnseSessionExpiredError):
                client.get("/test")


def test_set_trading_token_stores_token():
    """set_trading_token stores token for later use."""
    client = DnseClient(api_key="key", api_secret="secret")
    assert client._trading_token is None
    client.set_trading_token("token123")
    assert client._trading_token == "token123"
    client.close()
