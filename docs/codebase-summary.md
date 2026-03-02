# DNSE Python SDK - Codebase Summary

## Overview

DNSE is a production-ready Python SDK for the DNSE Open API with first-class support for both synchronous and asynchronous HTTP operations. Built with httpx, Pydantic v2, and strict typing for type safety and developer experience.

**Version:** 0.1.0 | **Python:** 3.10+ | **Status:** Foundation Complete

## Project Structure

```
src/dnse/
├── __init__.py              # Public API exports
├── _version.py              # Auto-generated version (hatch-vcs)
├── _http.py                 # HTTP utilities, headers, error handling
├── client.py                # DnseClient (sync)
├── async_client.py          # AsyncDnseClient (async)
├── exceptions.py            # Exception hierarchy
├── py.typed                 # PEP 561 marker for type support
└── models/
    ├── __init__.py
    └── base.py              # DnseBaseModel with camelCase alias support
```

## Key Components

### 1. HTTP Clients

**DnseClient** (Sync)
- Context manager support (`with DnseClient(...) as client:`)
- Methods: `get()`, `post()`, `put()`, `delete()`, `request()`
- Configurable base URL and timeout
- Bearer token authentication

**AsyncDnseClient** (Async)
- Same interface as sync, fully async
- Works with `async with` context managers
- Use when handling multiple concurrent requests

### 2. Exception Hierarchy

```
DnseError (base)
├── DnseAPIError (status_code, body)
│   ├── DnseAuthError (401/403)
│   └── DnseRateLimitError (429 + retry_after)
```

All exceptions automatically raised by response handler for non-2xx status codes.

### 3. Models

**DnseBaseModel**
- Pydantic v2 BaseModel with shared configuration
- Automatic snake_case ↔ camelCase conversion
- Supports both Python names and JSON keys

Example:
```python
class OrderInfo(DnseBaseModel):
    order_id: str
    total_amount: float

# Both work:
OrderInfo(order_id="123", total_amount=100.0)
OrderInfo(**{"orderId": "123", "totalAmount": 100.0})
```

### 4. HTTP Configuration

- **Base URL:** `https://openapi.dnse.com.vn` (TODO: confirm in API docs)
- **Timeout:** 30 seconds (configurable)
- **Headers:** User-Agent, Accept, Authorization (when api_key provided)
- **Auth:** Bearer token in `Authorization` header

## Testing & Quality

- **Coverage:** 98% (28 comprehensive tests)
- **Test Framework:** pytest + pytest-asyncio + respx (HTTP mocking)
- **Type Checking:** Strict mode (pyright)
- **Linting:** ruff with Google-style docstrings
- **CI/CD:** GitHub Actions (lint → type check → matrix test 3.10/3.11/3.12)

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| httpx | ≥0.27 | HTTP client (sync + async) |
| pydantic | ≥2 | Data validation & serialization |

## Development Workflow

```bash
uv sync              # Install deps in venv
uv run pytest        # Run tests with coverage
uv run ruff check .  # Lint check
uv run pyright       # Type check
uv build             # Build package (hatchling)
uv publish           # Publish to PyPI
```

## Release Process

- Versioning: Git tags → hatch-vcs → auto version in `_version.py`
- GitHub Actions workflow automates PyPI releases
- Currently at v0.1.0 (foundation/initial release)

## Known TODOs

1. Confirm actual DNSE API base URL (currently placeholder)
2. Confirm auth header format with DNSE API documentation
3. Add domain-specific response models when API spec available

## Next Steps

- Add typed response models as API endpoints are specified
- Consider adding request/response serialization helpers
- Add retries + backoff utilities for rate limit handling
