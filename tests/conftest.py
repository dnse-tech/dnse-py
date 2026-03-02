"""Shared test fixtures."""

import pytest
import respx

BASE_URL = "https://openapi.dnse.com.vn"


@pytest.fixture
def mock_api():
    """Mock the DNSE API with respx (sync + async compatible)."""
    with respx.mock(base_url=BASE_URL) as respx_mock:
        yield respx_mock
