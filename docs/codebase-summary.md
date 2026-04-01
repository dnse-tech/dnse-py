# DNSE Python SDK - Codebase Summary

## Overview

DNSE is a production-ready Python SDK for the DNSE Open API with first-class support for both synchronous and asynchronous HTTP operations. Built with httpx, Pydantic v2, and strict typing for type safety and developer experience.

**Version:** 0.2.0 | **Python:** 3.10+ | **Status:** Resource-Oriented API Complete

## Project Structure

```
src/dnse/
├── __init__.py              # Public API exports (clients, exceptions, models)
├── _version.py              # Auto-generated version (hatch-vcs)
├── _http.py                 # HTTP config, HMAC header building, error handling
├── _hmac_signer.py          # Stateless HMAC-SHA256 signing
├── _base_client.py          # BaseClient with retry, parsing, token injection
├── client.py                # DnseClient (sync) + resource properties
├── async_client.py          # AsyncDnseClient (async) + resource properties
├── exceptions.py            # Exception hierarchy + DnseSessionExpiredError
├── py.typed                 # PEP 561 marker for type support
├── models/
│   ├── __init__.py          # Export all models
│   ├── base.py              # DnseBaseModel with camelCase alias support
│   ├── auth.py              # TwoFARequest, TwoFAResponse
│   ├── accounts.py          # AccountItem, AccountsResponse, BalanceItem, etc.
│   ├── orders.py            # PlaceOrderRequest, OrderItem, OrdersResponse, etc.
│   ├── deals.py             # DealItem, DealsResponse
│   └── market.py            # SecurityDefinition, MarketResponse
└── resources/
    ├── __init__.py          # Export all resources
    ├── registration.py      # RegistrationResource, AsyncRegistrationResource
    ├── accounts.py          # AccountsResource, AsyncAccountsResource
    ├── orders.py            # OrdersResource, AsyncOrdersResource
    ├── deals.py             # DealsResource, AsyncDealsResource
    └── market.py            # MarketResource, AsyncMarketResource
```

## Key Components

### 1. HTTP Clients

**DnseClient** (Sync)
- Context manager support (`with DnseClient(api_key, api_secret) as client:`)
- Methods: `get()`, `post()`, `put()`, `delete()`, `request()`
- HMAC-SHA256 signing on all requests
- Auto-retry on 429 (rate limit) up to 3 attempts
- Trading token injection for order mutations
- Configurable base URL, timeout, date header
- Lazy-loaded resource properties: `client.orders`, `client.accounts`, `client.registration`, `client.deals`, `client.market`

**AsyncDnseClient** (Async)
- Same interface as sync, fully async
- Works with `async with` context manager
- Same resources, async variants
- Use when handling multiple concurrent requests

### 2. Exception Hierarchy

```
DnseError (base)
├── DnseAPIError (status_code, body)
│   ├── DnseAuthError (401/403 without trading token)
│   ├── DnseSessionExpiredError (401 with trading token set)
│   └── DnseRateLimitError (429 + retry_after + rate_limit_info)
```

All exceptions automatically raised by response handler for non-2xx status codes. `DnseSessionExpiredError` indicates trading token has expired; user must call `client.registration.verify_otp()` again.

### 3. Models & Resources

**DnseBaseModel** (Pydantic v2)
- Automatic snake_case ↔ camelCase conversion
- Supports both Python names and JSON keys

**Domain Models:**
- `models.auth`: `TwoFARequest`, `TwoFAResponse`
- `models.accounts`: `AccountItem`, `BalanceItem`, `LoanPackage`, `PpseResponse`, `AccountsResponse`
- `models.orders`: `PlaceOrderRequest`, `PlaceOrderResponse`, `OrderItem`, `OrdersResponse`, `UpdateOrderRequest`, `OrderHistoryResponse`
- `models.deals`: `DealItem`, `DealsResponse`
- `models.market`: `SecurityDefinition`, `Trade`, `MarketResponse`

**Resources** (accessed via client properties):
- `client.registration.send_otp()`, `client.registration.verify_otp(otp, otp_type)`
- `client.accounts.list()`, `client.accounts.balances(account_no)`, `client.accounts.loan_packages(account_no)`
- `client.orders.place(request)`, `client.orders.list(account_no)`, `client.orders.get(account_no, order_id)`, `client.orders.update()`, `client.orders.cancel()`, `client.orders.history()`
- `client.deals.list(account_no)`
- `client.market.security_info(symbol)`, `client.market.latest_trade(symbol, board_id)`, `client.market.trades(symbol, board_id, from_ts, to_ts, limit=None)`

### 4. HTTP Configuration & Authentication

- **Base URL:** `https://openapi.dnse.com.vn`
- **Timeout:** 30 seconds (configurable)
- **Auth:** HMAC-SHA256 signing with `api_key` and `api_secret`
- **Headers:**
  - `x-api-key`: API key
  - `X-Signature`: HMAC-SHA256 signature
  - `Date` or `X-Aux-Date`: RFC 2822 timestamp (configurable)
  - `nonce`: UUID4 hex (included in signature)
  - `trading-token`: OTP-derived token (order mutations only)

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

## Completed Features (v0.2.0)

- HMAC-SHA256 request signing with nonce and configurable date header
- Resource-oriented API with lazy-loaded property access
- Automatic 429 retry up to 3 attempts with exponential backoff
- OTP/trading token flow with session expiry detection
- Typed Pydantic v2 models for all API endpoints
- Full request/response serialization with snake_case ↔ camelCase
- 90%+ test coverage with strict type checking

## Next Steps (v0.3+)

- Request/response logging and tracing
- Webhook validation helpers
- CLI tool for API exploration
- WebSocket support for real-time market data
- Streaming response bodies
