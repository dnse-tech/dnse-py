"""Tests for _http.py configuration and response handling."""

import pytest

from dnse._http import HttpConfig, build_request_headers, handle_response
from dnse.exceptions import DnseAPIError, DnseAuthError, DnseRateLimitError, DnseSessionExpiredError


def test_build_request_headers_with_credentials():
    config = HttpConfig(api_key="mykey", api_secret="mysecret")
    headers = build_request_headers("GET", "/accounts", config)
    assert headers["x-api-key"] == "mykey"
    assert "X-Signature" in headers
    assert "date" in headers
    assert headers["Accept"] == "application/json"
    assert "User-Agent" in headers


def test_build_request_headers_without_credentials():
    config = HttpConfig()
    headers = build_request_headers("GET", "/accounts", config)
    assert "x-api-key" not in headers
    assert "X-Signature" not in headers
    assert headers["Accept"] == "application/json"


def test_build_request_headers_custom_date_header():
    config = HttpConfig(api_key="k", api_secret="s", date_header="x-aux-date")
    headers = build_request_headers("GET", "/accounts", config)
    assert "x-aux-date" in headers
    assert "date" not in headers


def test_handle_response_2xx_passes():
    for code in (200, 201, 204, 299):
        handle_response(code, "")  # must not raise


def test_handle_response_401_raises_auth_error():
    with pytest.raises(DnseAuthError) as exc_info:
        handle_response(401, "Unauthorized")
    assert exc_info.value.status_code == 401
    assert exc_info.value.body == "Unauthorized"


def test_handle_response_403_raises_auth_error():
    with pytest.raises(DnseAuthError) as exc_info:
        handle_response(403, "Forbidden")
    assert exc_info.value.status_code == 403


def test_handle_response_401_session_expired():
    body = '{"code": "INVALID_TRADING_TOKEN", "message": "Token expired"}'
    with pytest.raises(DnseSessionExpiredError) as exc_info:
        handle_response(401, body, trading_token_set=True)
    assert exc_info.value.status_code == 401


def test_handle_response_401_no_token_not_session_expired():
    """Without trading token, 401 is always DnseAuthError, not DnseSessionExpiredError."""
    body = '{"code": "INVALID_TRADING_TOKEN", "message": "Token expired"}'
    with pytest.raises(DnseAuthError) as exc_info:
        handle_response(401, body, trading_token_set=False)
    assert type(exc_info.value) is not DnseSessionExpiredError


def test_handle_response_429_raises_rate_limit_error():
    with pytest.raises(DnseRateLimitError) as exc_info:
        handle_response(429, "Too Many Requests")
    assert exc_info.value.status_code == 429
    assert exc_info.value.retry_after is None


def test_handle_response_429_parses_retry_after():
    with pytest.raises(DnseRateLimitError) as exc_info:
        handle_response(429, "Too Many Requests", {"retry-after": "5"})
    assert exc_info.value.retry_after == 5.0


def test_handle_response_429_non_numeric_retry_after():
    with pytest.raises(DnseRateLimitError) as exc_info:
        handle_response(429, "Too Many Requests", {"retry-after": "Wed, 21 Oct 2026 07:28:00 GMT"})
    assert exc_info.value.retry_after is None


def test_handle_response_500_raises_api_error():
    with pytest.raises(DnseAPIError) as exc_info:
        handle_response(500, "Internal Server Error")
    assert exc_info.value.status_code == 500
    assert type(exc_info.value) is DnseAPIError
