"""Tests for exception hierarchy."""

from dnse.exceptions import DnseAPIError, DnseAuthError, DnseError, DnseRateLimitError


def test_exception_hierarchy():
    assert issubclass(DnseAPIError, DnseError)
    assert issubclass(DnseAuthError, DnseAPIError)
    assert issubclass(DnseRateLimitError, DnseAPIError)


def test_api_error_attributes():
    err = DnseAPIError(404, "Not Found")
    assert err.status_code == 404
    assert err.body == "Not Found"
    assert "404" in str(err)
    assert "Not Found" in str(err)


def test_rate_limit_error_retry_after():
    err = DnseRateLimitError(429, "Too Many Requests", retry_after=10.0)
    assert err.status_code == 429
    assert err.retry_after == 10.0

    err_no_retry = DnseRateLimitError(429, "Too Many Requests")
    assert err_no_retry.retry_after is None
