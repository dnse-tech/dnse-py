"""Tests for _http.py pure functions."""

import pytest

from dnse._http import HttpConfig, build_headers, handle_response
from dnse.exceptions import DnseAPIError, DnseAuthError, DnseRateLimitError


def test_build_headers_with_api_key():
    config = HttpConfig(api_key="secret")
    headers = build_headers(config)
    assert headers["Authorization"] == "Bearer secret"
    assert headers["Accept"] == "application/json"
    assert "User-Agent" in headers


def test_build_headers_without_api_key():
    config = HttpConfig()
    headers = build_headers(config)
    assert "Authorization" not in headers
    assert headers["Accept"] == "application/json"


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
    # DnseAPIError but NOT a subclass
    assert type(exc_info.value) is DnseAPIError
