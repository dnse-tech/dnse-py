# DNSE Python SDK - Project Overview & PDR

## Executive Summary

DNSE Python SDK is a production-ready, type-safe HTTP client library for the DNSE Open API. The foundation includes dual sync/async HTTP clients, comprehensive error handling, Pydantic v2 models with camelCase support, and 98% test coverage with strict type checking.

**Project Phase:** Resource-Oriented API Complete (v0.2.0)
**Team:** DNSE Tech
**Target Users:** Python developers integrating with DNSE Open API for trading, account management, and market data

## Product Development Requirements (PDR)

### Functional Requirements

#### FR-1: HTTP Client Operations (COMPLETE)
- Dual sync (`DnseClient`) and async (`AsyncDnseClient`) clients
- RESTful HTTP methods: GET, POST, PUT, DELETE, generic request()
- Context manager support for resource cleanup
- HMAC-SHA256 authentication on all requests
- Configurable base URL, timeout, date header
- Request nonce auto-generation

#### FR-2: Authentication (COMPLETE)
- HMAC-SHA256 signing with `api_key` and `api_secret`
- Automatic x-api-key, X-Signature, Date/X-Aux-Date headers
- OTP-based trading token flow via `client.registration.verify_otp()`
- Session expiry detection: 401 with token → `DnseSessionExpiredError`
- Transparent token injection for order mutations

#### FR-3: Error Handling (COMPLETE)
- Typed exception hierarchy: `DnseError` → `DnseAPIError` → (`DnseAuthError`, `DnseSessionExpiredError`, `DnseRateLimitError`)
- Automatic exception raising for non-2xx status codes
- Rate limit error includes retry-after seconds
- Session expiry distinguished from invalid credentials
- Auth errors for 401/403, API errors for others

#### FR-4: Response Models (COMPLETE)
- Pydantic v2 BaseModel (`DnseBaseModel`) with camelCase support
- Domain models for all endpoints: Auth, Accounts, Orders, Deals, Market
- Automatic snake_case ↔ camelCase conversion
- Type-safe request/response validation and serialization

#### FR-5: Resource-Oriented API (COMPLETE)
- Namespaced resource access: `client.registration`, `client.accounts`, `client.orders`, `client.deals`, `client.market`
- Lazy-loaded `@cached_property` resources
- Intuitive method naming: `client.orders.place()`, `client.accounts.list()`, `client.deals.list()`
- Full CRUD support for orders (place, list, get, update, cancel, history)

#### FR-6: Reliability (COMPLETE)
- Auto-retry on 429 (rate limit) up to 3 attempts with exponential backoff
- Respects `retry-after` header if provided
- No transparent re-auth (OTP is manual, user-driven)

#### FR-7: Developer Experience (COMPLETE)
- Type hints throughout (strict pyright mode)
- Google-style docstrings for all public APIs
- Intuitive sync/async API consistency
- Clear exception messages with context

### Non-Functional Requirements

#### NFR-1: Quality & Testing (COMPLETE)
- 90%+ code coverage across all modules
- Unit tests for HMAC signer, base client, all models, resources
- Integration tests with HTTP mocking (respx)
- Async test support (pytest-asyncio)
- All tests passing across Python 3.10/3.11/3.12
- Deterministic retry and backoff tests

#### NFR-2: Type Safety (COMPLETE)
- Strict type checking (pyright strict mode)
- PEP 561 compliance (py.typed marker)
- Full type hints in all modules including resources
- No untyped code or Any abuse

#### NFR-3: Code Quality (COMPLETE)
- Ruff linting: E, F, I, B, UP, D, S rules
- Google-style docstring convention
- Line length limit: 100 characters
- Pre-commit validation ready
- Modular, focused files (all under 200 LOC)

#### NFR-4: Maintainability (COMPLETE)
- Clear layered architecture: Resource → Client → BaseClient → HMAC → HTTP → Transport
- Reusable utilities in _http.py, _hmac_signer.py
- DRY principle applied (base client shared logic, models configuration)
- Separation of concerns (resources don't handle auth headers)

#### NFR-5: Performance & Reliability (COMPLETE)
- Efficient httpx-based HTTP layer with connection pooling
- Exponential backoff for rate limiting (2^attempt * base_delay)
- Timeout handling (30s default, configurable)
- Proper resource cleanup (context managers)
- No blocking calls in async code path

#### NFR-6: Release & Distribution (COMPLETE)
- Automated versioning via hatch-vcs + git tags
- GitHub Actions CI pipeline (lint → type → test matrix)
- PyPI publishing workflow automation
- Semantic versioning (0.2.0 with breaking api_secret requirement)

### Technical Constraints

1. **Python Version:** 3.10+ (matches project requirement)
2. **Dependencies:** httpx ≥0.27, pydantic ≥2 (minimal, stable)
3. **Type Checking:** Strict mode, no Any without justification
4. **Line Length:** 100 characters (ruff config)
5. **Docstrings:** Google convention required

## Architecture

### Layer Model

```
┌─────────────────────────────────────┐
│   Application Layer                 │
│   (User's code using SDK)           │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   Client Layer                      │
│  DnseClient | AsyncDnseClient       │
│  (Interface & public API)           │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   HTTP Layer (_http.py)             │
│  - HttpConfig, headers, error map   │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   Transport Layer                   │
│   httpx.Client / httpx.AsyncClient  │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   Network (DNSE API)                │
└─────────────────────────────────────┘

Models (Pydantic) - Orthogonal
└─ DnseBaseModel for response unmarshaling
```

## Success Metrics (v0.2.0)

- [x] 90%+ code coverage achieved
- [x] Strict type checking passing (pyright)
- [x] All linting rules satisfied (ruff)
- [x] Tests passing on 3.10, 3.11, 3.12
- [x] CI pipeline green
- [x] HMAC-SHA256 signing implemented and tested
- [x] OTP/trading token flow working
- [x] Resource-oriented API complete
- [x] Retry logic on 429 with exponential backoff
- [x] Session expiry detection implemented
- [x] All domain models typed and tested
- [x] Sync and async resources consistent
- [x] Package buildable and publishable
- [x] Documentation updated

## Future Roadmap (v0.3+)

1. **Logging & Tracing:** Structured logging with DEBUG level support
2. **Hooks/Middleware:** Request/response interceptors for custom handling
3. **Streaming:** Support for streaming response bodies
4. **Webhook Validation:** Helpers for validating incoming webhook signatures
5. **CLI Tool:** Command-line interface for exploring API endpoints
6. **Real-Time Data:** WebSocket support for market data streams
7. **Batch Operations:** Helper methods for bulk order/account operations

## Development Standards

See `/docs/code-standards.md` for implementation patterns, module organization, and contribution guidelines.

See `/docs/system-architecture.md` for deployment, integration, and infrastructure details.
