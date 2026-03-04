# Changelog

All notable changes to the DNSE Python SDK project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2026-03-04

### Changed

- **README**: Updated to document WebSocket streaming (`DnseMarketStream`, `DnseTradingStream`), stream message models, `orders.get()` / `orders.update()`, `accounts.ppse()`, `otp_type` parameter, and market enums

---

## [0.3.0] - 2026-03-04

### Added

- **WebSocket Streaming**: Real-time market data and trading event subscriptions via `AsyncDnseClient.stream`
  - `client.stream.market_data(symbols)` — live quotes and order book updates
  - `client.stream.trading_events()` — order fill and status change notifications
- **Typed Market Enums**: `MarketId`, `ProductGrpId`, `SecurityGroupId`, `SecurityStatus` for type-safe market data filtering
- **Typed `BoardId`** field on `SecurityDefinition` (previously untyped `str`)
- **`MarketType` parameter** on `client.accounts.loan_packages()` and `client.deals.list()`
- **`OtpType` enum** for explicit OTP method selection (`EMAIL`, `SMART_OTP`)
- **`metadata` and `error` fields** on `OrderItem` and `PlaceOrderResponse` — exposes rejection reason (e.g. `QMAX_EXCEED`) and raw server metadata
- **Integration test suite** with `respx`-based HTTP mocking covering the full request pipeline
- **Comprehensive async tests** for streaming and resource layers

### Fixed

- **Trading token not sent on `update()` and `cancel()`** — path check was `/accounts/orders` (only matched `place`), changed to `/orders` to cover all order mutation endpoints
- **`JSONDecodeError` on order detail responses** — server embeds unescaped JSON objects in the `metadata` string field; responses are now sanitized before parsing
- **Double-headers bug** in low-level HTTP request methods

### Changed

- `client.deals.list()` now requires `market_type` as an explicit keyword argument (previously accepted as `**kwargs`)
- Order `update()` docstring documents DNSE cancel-then-replace behaviour: the returned `OrderItem.id` is a **new** order ID; callers must use it for subsequent `get()`/`cancel()` calls

---

## [0.2.0] - 2026-03-03

### Added

- **Resource Layer API**: Comprehensive resource-based SDK with fluent interface
  - `client.accounts.list()` - List user accounts
  - `client.accounts.balances(account_no)` - Get account balances
  - `client.accounts.loan_packages(account_no)` - Get loan packages
  - `client.orders.place(PlaceOrderRequest)` - Place orders
  - `client.orders.list(account_no, marketType, orderCategory)` - List active orders
  - `client.orders.history(account_no, from, to)` - Get order history
  - `client.orders.cancel(account_no, order_id)` - Cancel orders
  - `client.deals.list(account_no)` - List deals
  - `client.market.security_info(symbol)` - Get security information
- **Domain-Driven Models**: Organized Pydantic v2 models in domain packages
  - `dnse.models.auth` - Authentication models (TwoFARequest, TwoFAResponse)
  - `dnse.models.account` - Account models (AccountsResponse, AccountBalanceResponse, LoanPackageResponse)
  - `dnse.models.order` - Order models (PlaceOrderRequest, PlaceOrderResponse, GetOrdersResponse, OrderHistoryResponse)
  - `dnse.models.deal` - Deal models (DealsResponse, DealItem)
  - `dnse.models.market` - Market models (SecurityDefinition)
- **Exception Hierarchy**: New specific exception types
  - `DnseSessionExpiredError` - For expired trading tokens
  - `DnseRateLimitError` - For rate limiting with retry_after metadata
  - `DnseAuthError` - For authentication failures
  - `DnseAPIError` - For API-level errors with status_code and body
- **Async Support**: Full async/await SDK via `AsyncDnseClient`
  - Parallel request handling with httpx async transport
  - Compatible with asyncio event loops
- **Request/Response Handling**
  - Automatic HMAC-SHA256 signature generation
  - Configurable date header (date or x-aux-date)
  - Request/response logging and debugging
  - Strict Pydantic v2 validation with mode="python"
- **Retry Logic & Resilience**
  - Automatic exponential backoff for transient failures
  - Configurable timeout per request (default 30s)
  - Connection pooling via httpx HTTPClient
- **Context Manager Support**
  - `with DnseClient(...) as client:` for sync
  - `async with AsyncDnseClient(...) as client:` for async
  - Automatic resource cleanup

### Changed

- **Complete SDK Reorganization**
  - Refactored from minimal foundation to production-ready SDK
  - Moved from single-file models to organized domain packages
  - Enhanced from basic exception handling to granular error types
- **Authentication Flow**
  - Two-factor authentication via OTP (email-based)
  - Trading token management for mutations
  - Automatic auth header injection with timestamps
- **Request Headers**
  - Added HMAC-SHA256 signature header
  - Added date/x-aux-date header for request timing
  - Added user-agent identification

### Fixed

- None (initial complete version)

### Removed

- None (initial complete version)

### Security

- **HMAC-SHA256 Authentication**: All requests signed with API secret
- **Pydantic Validation**: Strict v2 validation prevents injection attacks
- **Timeout Protection**: All requests have configurable timeout (default 30s)
- **Type Safety**: 100% typed codebase with pyright strict mode

---

## [0.1.0] - 2026-03-02

### Added

- **Project Scaffolding**: Initial Python SDK structure with uv package manager
  - pyproject.toml configuration with hatch-vcs versioning
  - uv.lock dependency lock file
  - .gitignore with Python/IDE patterns
- **Core SDK Foundation**
  - Base client implementation with httpx HTTP transport
  - Sync client (`DnseClient`) and async client (`AsyncDnseClient`)
  - Exception base classes (`DnseError`, `DnseAPIError`, `DnseAuthError`, `DnseRateLimitError`)
- **Basic Models**
  - `DnseBaseModel` using Pydantic v2
  - Initial request/response model stubs
- **Development Setup**
  - pytest with async support (pytest-asyncio)
  - Code quality tools: ruff linter, pyright type checker
  - Test coverage reporting (pytest-cov)
  - HTTP mocking for tests (respx)
- **Documentation**
  - README with installation, quickstart, and configuration
  - System architecture documentation
  - SDK API reference documentation

### Changed

- None (initial version)

### Fixed

- None (initial version)

### Removed

- None (initial version)

### Security

- None (initial version)

---

## Unreleased

### Planned Features

- [ ] WebSocket support for real-time market data
- [ ] Batch order operations
- [ ] Advanced order types (stop-loss, trailing stop)
- [ ] Portfolio analytics and reporting
- [ ] Request caching layer
- [ ] SDK metrics and observability
- [ ] CLI tool for DNSE API interaction
- [ ] Documentation site generation

### Known Limitations

- WebSocket connections not yet supported
- Some advanced order validation rules pending API spec clarification
- Rate limit handling is basic (no adaptive backoff)

