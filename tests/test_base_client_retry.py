"""Tests for retry logic in BaseClient._request_with_retry."""

from unittest.mock import patch

import httpx
import pytest
import respx

from dnse.client import DnseClient
from dnse.exceptions import DnseRateLimitError

BASE_URL = "https://openapi.dnse.com.vn"


def test_retry_429_once_then_success():
    """Single 429 followed by 200 succeeds after retry."""
    with respx.mock(base_url=BASE_URL) as mock:
        # First call returns 429, second returns 200
        mock.get("/accounts").mock(
            side_effect=[
                httpx.Response(429, text="Too Many Requests"),
                httpx.Response(200, json={"status": "ok"}),
            ]
        )
        with DnseClient() as client:
            response = client.get("/accounts")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_retry_429_exhausted():
    """After 3 429 responses, raises DnseRateLimitError."""
    with respx.mock(base_url=BASE_URL) as mock:
        # All calls return 429
        mock.get("/accounts").mock(return_value=httpx.Response(429, text="Too Many Requests"))
        with DnseClient() as client:
            with pytest.raises(DnseRateLimitError) as exc_info:
                client.get("/accounts")
        assert exc_info.value.status_code == 429


def test_retry_respects_retry_after_header():
    """Retry-After header value is used for sleep duration."""
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/accounts").mock(
            side_effect=[
                httpx.Response(429, text="Rate limited", headers={"retry-after": "2"}),
                httpx.Response(200, json={"data": "ok"}),
            ]
        )
        with patch("time.sleep") as mock_sleep:
            with DnseClient() as client:
                response = client.get("/accounts")
            # sleep should have been called with 2.0 (from retry-after header)
            mock_sleep.assert_called()
            # The call should be 2.0 seconds
            calls = mock_sleep.call_args_list
            assert any(call[0][0] == 2.0 for call in calls)
        assert response.status_code == 200


def test_retry_with_exponential_backoff():
    """When retry-after not set, exponential backoff is used."""
    with respx.mock(base_url=BASE_URL) as mock:
        # Multiple 429s without retry-after header
        mock.get("/test").mock(return_value=httpx.Response(429, text="Rate limited"))
        with patch("time.sleep") as mock_sleep:
            with DnseClient() as client:
                with pytest.raises(DnseRateLimitError):
                    client.get("/test")
            # Sleep should be called with exponential backoff: 1.0, 2.0, etc.
            calls = mock_sleep.call_args_list
            assert len(calls) == 2  # MAX_RETRIES - 1 = 2
            # First call: 1.0 * (2^0) = 1.0
            # Second call: 1.0 * (2^1) = 2.0
            assert calls[0][0][0] == 1.0
            assert calls[1][0][0] == 2.0


def test_no_retry_on_200():
    """200 response does not trigger retry."""
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/accounts").mock(return_value=httpx.Response(200, json={"accounts": []}))
        with patch("time.sleep") as mock_sleep:
            with DnseClient() as client:
                response = client.get("/accounts")
            # No sleep calls should happen
            mock_sleep.assert_not_called()
        assert response.status_code == 200


def test_no_retry_on_401():
    """401 response does not trigger retry."""
    from dnse.exceptions import DnseAuthError

    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/accounts").mock(return_value=httpx.Response(401, text="Unauthorized"))
        with patch("time.sleep") as mock_sleep:
            with DnseClient() as client:
                with pytest.raises(DnseAuthError):
                    client.get("/accounts")
            # No sleep calls should happen
            mock_sleep.assert_not_called()


def test_no_retry_on_404():
    """404 response does not trigger retry."""
    from dnse.exceptions import DnseAPIError

    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/accounts").mock(return_value=httpx.Response(404, text="Not Found"))
        with patch("time.sleep") as mock_sleep:
            with DnseClient() as client:
                with pytest.raises(DnseAPIError):
                    client.get("/accounts")
            # No sleep calls should happen
            mock_sleep.assert_not_called()


def test_retry_non_numeric_retry_after():
    """Non-numeric retry-after falls back to exponential backoff."""
    with respx.mock(base_url=BASE_URL) as mock:
        mock.get("/accounts").mock(
            side_effect=[
                httpx.Response(
                    429,
                    text="Rate limited",
                    headers={"retry-after": "Wed, 21 Oct 2026 07:28:00 GMT"},
                ),
                httpx.Response(200, json={"ok": True}),
            ]
        )
        with patch("time.sleep") as mock_sleep:
            with DnseClient() as client:
                response = client.get("/accounts")
            # Should use exponential backoff (1.0) since retry-after is not numeric
            mock_sleep.assert_called_with(1.0)
        assert response.status_code == 200


def test_handle_retry_returns_none_for_non_429():
    """_handle_retry returns None for non-429 responses."""
    with DnseClient() as client:
        response = httpx.Response(200, json={"ok": True})
        result = client._handle_retry(0, response)
        assert result is None


def test_handle_retry_returns_float_for_429():
    """_handle_retry returns float for 429 responses."""
    with DnseClient() as client:
        response = httpx.Response(429, text="Too Many Requests")
        result = client._handle_retry(0, response)
        assert isinstance(result, float)
        assert result > 0


def test_handle_retry_respects_header():
    """_handle_retry extracts retry-after header value."""
    with DnseClient() as client:
        response = httpx.Response(429, text="Too Many Requests", headers={"retry-after": "5"})
        result = client._handle_retry(0, response)
        assert result == 5.0
