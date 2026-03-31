"""Tests for RateLimitInfo dataclass and parse_rate_limit_info factory."""

from unittest.mock import patch

import pytest

from dnse._http import RateLimitInfo, parse_rate_limit_info


class TestRateLimitInfo:
    def test_construction_all_fields(self):
        info = RateLimitInfo(limit=100, remaining=50, reset_at=1711900800)
        assert info.limit == 100
        assert info.remaining == 50
        assert info.reset_at == 1711900800

    def test_construction_defaults_none(self):
        info = RateLimitInfo()
        assert info.limit is None
        assert info.remaining is None
        assert info.reset_at is None

    def test_frozen(self):
        info = RateLimitInfo(limit=100)
        with pytest.raises(AttributeError):
            info.limit = 200  # type: ignore[misc]

    def test_seconds_until_reset_none(self):
        info = RateLimitInfo()
        assert info.seconds_until_reset == 0.0

    def test_seconds_until_reset_future(self):
        with patch("dnse._http.time") as mock_time:
            mock_time.time.return_value = 1000.0
            info = RateLimitInfo(reset_at=1060)
            assert info.seconds_until_reset == 60.0

    def test_seconds_until_reset_past(self):
        with patch("dnse._http.time") as mock_time:
            mock_time.time.return_value = 2000.0
            info = RateLimitInfo(reset_at=1000)
            assert info.seconds_until_reset == 0.0


class TestParseRateLimitInfo:
    def test_all_headers_present(self):
        headers = {
            "x-ratelimit-limit": "100",
            "x-ratelimit-remaining": "99",
            "x-ratelimit-reset": "1711900800",
        }
        info = parse_rate_limit_info(headers)
        assert info is not None
        assert info.limit == 100
        assert info.remaining == 99
        assert info.reset_at == 1711900800

    def test_partial_headers(self):
        info = parse_rate_limit_info({"x-ratelimit-remaining": "42"})
        assert info is not None
        assert info.limit is None
        assert info.remaining == 42
        assert info.reset_at is None

    def test_no_headers_returns_none(self):
        assert parse_rate_limit_info({}) is None

    def test_irrelevant_headers_returns_none(self):
        assert parse_rate_limit_info({"content-type": "application/json"}) is None

    def test_invalid_values_become_none(self):
        headers = {
            "x-ratelimit-limit": "not-a-number",
            "x-ratelimit-remaining": "99",
        }
        info = parse_rate_limit_info(headers)
        assert info is not None
        assert info.limit is None
        assert info.remaining == 99

    def test_case_insensitive(self):
        headers = {
            "X-RateLimit-Limit": "100",
            "X-RATELIMIT-REMAINING": "50",
            "x-ratelimit-reset": "1711900800",
        }
        info = parse_rate_limit_info(headers)
        assert info is not None
        assert info.limit == 100
        assert info.remaining == 50
        assert info.reset_at == 1711900800

    def test_all_invalid_returns_none(self):
        headers = {
            "x-ratelimit-limit": "abc",
            "x-ratelimit-remaining": "",
            "x-ratelimit-reset": "xyz",
        }
        assert parse_rate_limit_info(headers) is None
