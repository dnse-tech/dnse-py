# DNSE Python SDK - Code Standards

## File Organization

```
src/dnse/
├── __init__.py              # Public API only (__all__ exports)
├── _http.py                 # HTTP utilities (private, for internal use)
├── client.py                # DnseClient (sync)
├── async_client.py          # AsyncDnseClient (async)
├── exceptions.py            # Exception classes
├── py.typed                 # PEP 561 marker
└── models/
    ├── __init__.py
    └── base.py              # DnseBaseModel

tests/
├── test_client.py           # DnseClient sync tests
├── test_async_client.py     # AsyncDnseClient async tests
├── test_exceptions.py       # Exception hierarchy tests
├── test_http.py             # HTTP utilities tests
├── test_models.py           # Model serialization tests
└── integration/             # Full-pipeline integration tests (respx mocked HTTP)
    ├── __init__.py
    ├── conftest.py          # Shared constants & fixtures (BASE_URL, FAKE_KEY, FAKE_SECRET)
    ├── test_auth_pipeline.py        # Auth headers, HMAC signing, trading-token rules
    ├── test_sync_pipeline.py        # Sync resources: registration, accounts, orders, deals, market
    └── test_async_pipeline.py       # Async resources: registration, accounts, orders, deals, market
```

## Naming Conventions

| Category | Convention | Example |
|----------|-----------|---------|
| Modules | snake_case | `_http.py`, `async_client.py` |
| Classes | PascalCase | `DnseClient`, `HttpConfig` |
| Functions | snake_case | `build_headers()`, `handle_response()` |
| Constants | UPPER_CASE | `DEFAULT_BASE_URL` |
| Private | _leading_underscore | `_http.py`, `_client`, `_version.py` |
| Tests | test_*.py | `test_client.py`, `test_exceptions.py` |

## Import Organization

All modules follow this order:
```python
"""Module docstring."""

from __future__ import annotations  # PEP 563

from typing import Any              # Standard library typing
from dataclasses import dataclass   # Standard library

import httpx                        # Third-party

from dnse._http import build_headers  # Relative local imports
from dnse.exceptions import DnseError
```

## Type Hints

### Rules
- **Always** annotate function parameters and return types
- **Always** use `from __future__ import annotations` for forward refs
- **Never** use `Any` without explicit comment justifying it
- Use `|` for union types (Python 3.10+), not `Union`
- Optional types: use `X | None`, not `Optional[X]`

### Examples
```python
def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
    """Send an HTTP request.

    Args:
        method: HTTP verb.
        path: URL path.
        **kwargs: Forwarded to httpx (Any for variadic kwargs is acceptable).

    Returns:
        Response object.
    """
```

## Docstrings (Google Style)

### Module Level
```python
"""Module purpose in one line.

Detailed explanation if needed, spanning multiple paragraphs.
Can reference related modules or classes.
"""
```

### Class Level
```python
class DnseClient:
    """One-line summary.

    Extended description with usage examples if complex.
    Explain key behavior, invariants, or notable patterns.

    Attributes:
        Optional, only if class has public attributes to document.
    """
```

### Function Level
```python
def build_headers(config: HttpConfig) -> dict[str, str]:
    """Build request headers including auth if api_key is set.

    Args:
        config: HTTP client configuration.

    Returns:
        Dictionary of HTTP headers.

    Raises:
        ValueError: If config is invalid (if applicable).
    """
```

## Error Handling

### Exception Hierarchy
```python
class DnseError(Exception):
    """Base exception for DNSE SDK."""

class DnseAPIError(DnseError):
    """API returned an error response."""
    def __init__(self, status_code: int, body: str) -> None: ...

class DnseAuthError(DnseAPIError):
    """Authentication failed (401/403)."""

class DnseRateLimitError(DnseAPIError):
    """Rate limited (429)."""
    def __init__(
        self, status_code: int, body: str,
        retry_after: float | None = None,
        rate_limit_info: RateLimitInfo | None = None,
    ) -> None: ...
```

### Usage in Code
```python
try:
    response = client.get("/v1/endpoint")
except DnseAuthError:
    # Handle authentication failure
    pass
except DnseRateLimitError as e:
    # Exponential backoff using e.retry_after
    # Access rate limit details via e.rate_limit_info
    if e.rate_limit_info:
        print(f"{e.rate_limit_info.remaining}/{e.rate_limit_info.limit}")
    pass
except DnseAPIError as e:
    # Other API errors (access status_code, body)
    pass
```

### Rate Limit Info
```python
from dnse import parse_rate_limit_info

# Parse rate limit headers from any successful response
info = parse_rate_limit_info(dict(response.headers))
if info and info.remaining is not None and info.remaining < 10:
    print(f"Quota low — resets in {info.seconds_until_reset:.0f}s")
```

## Model Design (Pydantic v2)

### Base Model Pattern
```python
from dnse.models import DnseBaseModel

class OrderInfo(DnseBaseModel):
    """Order information from API.

    Automatically converts between snake_case (Python)
    and camelCase (API JSON).
    """
    order_id: str
    total_amount: float
    created_at: str
```

### Key Features
- Inherits from `DnseBaseModel` (not raw `BaseModel`)
- `populate_by_name=True` enables both naming conventions
- `alias_generator=to_camel` auto-converts field names
- Full Pydantic v2 validation and serialization

## Client Implementation

### Sync Pattern
```python
with DnseClient(api_key="key") as client:
    try:
        response = client.get("/v1/endpoint")
        data = response.json()
    except DnseAuthError:
        # Handle error
        pass
```

### Async Pattern
```python
async with AsyncDnseClient(api_key="key") as client:
    try:
        response = await client.get("/v1/endpoint")
        data = response.json()
    except DnseRateLimitError as e:
        await asyncio.sleep(e.retry_after or 1.0)
```

## Testing Standards

### Coverage Target
- 95%+ code coverage (currently 98%)
- All public methods tested
- Error paths tested
- Edge cases covered
- Full-pipeline integration tests via respx transport mocking

### Test Types

#### Unit Tests (tests/test_*.py)
Mock `_send()` and `_async_send()` methods; verify isolated component behavior.

#### Integration Tests (tests/integration/)
Full-pipeline tests using `respx.mock` context manager; verify HMAC signing, headers, body serialization, and response parsing through real httpx transport without modifying SDK internals.

### Test Structure
```python
# Unit test example: test_client.py
import pytest
from dnse import DnseClient, DnseAuthError

def test_get_success(respx_mock):
    """Test successful GET request."""
    respx_mock.get("https://example.com/v1/test").mock(
        return_value=httpx.Response(200, json={"key": "value"})
    )
    with DnseClient() as client:
        response = client.get("/v1/test")
        assert response.status_code == 200

def test_auth_error_on_401(respx_mock):
    """Test that 401 raises DnseAuthError."""
    respx_mock.get("https://example.com/v1/test").mock(
        return_value=httpx.Response(401, text="Unauthorized")
    )
    with DnseClient() as client:
        with pytest.raises(DnseAuthError):
            client.get("/v1/test")
```

#### Integration Test Pattern (tests/integration/)
```python
# tests/integration/test_auth_pipeline.py
import respx
from dnse import DnseClient
from tests.integration.conftest import BASE_URL, FAKE_KEY, FAKE_SECRET

def test_hmac_headers_present():
    """Verify HMAC auth headers on authenticated request via respx transport."""
    with respx.mock:
        respx.get(f"{BASE_URL}/accounts").mock(
            return_value=httpx.Response(200, json={"accounts": []})
        )
        # DnseClient instantiated INSIDE respx.mock context to capture transport
        client = DnseClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET)
        client.accounts.list()

        # Inspect intercepted request
        request = respx.calls.last.request
        assert request.headers["x-api-key"] == FAKE_KEY
        assert "x-signature" in request.headers
        assert "date" in request.headers
        assert "nonce" in request.headers
```

### Test Fixtures
- Use `respx.mock` for HTTP mocking (respx intercepts httpx.Client transport)
- Use `pytest-asyncio` with `asyncio_mode = "auto"` (async tests auto-discovered)
- Factory fixtures for common test data
- Parameterized tests for multiple scenarios
- Shared fixtures in `tests/integration/conftest.py` (BASE_URL, FAKE_KEY, FAKE_SECRET, FAKE_ACCOUNT)

## Linting & Type Checking

### Ruff Configuration (pyproject.toml)
```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "D", "S"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "D"]  # Allow assertions + no docstrings
```

### Pyright Configuration (pyproject.toml)
```toml
[tool.pyright]
typeCheckingMode = "strict"
pythonVersion = "3.10"

[[tool.pyright.executionEnvironments]]
root = "tests"
reportPrivateUsage = "none"
```

## Pre-commit Checklist

Before committing code:

1. **Linting:** `uv run ruff check . --fix`
2. **Type Check:** `uv run pyright` (no errors)
3. **Tests:** `uv run pytest --cov=src/dnse` (98%+ coverage)
4. **Format:** `uv run ruff format .` (optional, covered by check)

## Performance Considerations

1. **Connection Pooling:** httpx.Client maintains connection pool
2. **Timeout:** Default 30s, configurable per client
3. **No Blocking Ops:** Async client for concurrent requests
4. **Memory:** Proper client.close() or context manager usage

## Security Best Practices

1. **API Keys:** Never hardcode, always use environment variables
2. **Secrets:** Never log auth headers or response bodies with credentials
3. **HTTPS Only:** All DNSE API calls use HTTPS
4. **Validation:** Pydantic validates all incoming data
5. **Type Safety:** Strict typing prevents injection attacks

## Documentation Requirements

- All public methods must have docstrings
- All classes must have docstrings
- All modules must have module-level docstrings
- Use examples in docstrings for complex APIs
- Link to related modules/classes when helpful
