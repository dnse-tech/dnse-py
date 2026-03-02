# DNSE Python SDK - Project Overview & PDR

## Executive Summary

DNSE Python SDK is a production-ready, type-safe HTTP client library for the DNSE Open API. The foundation includes dual sync/async HTTP clients, comprehensive error handling, Pydantic v2 models with camelCase support, and 98% test coverage with strict type checking.

**Project Phase:** Foundation Complete (v0.1.0)
**Team:** DNSE Tech
**Target Users:** Python developers integrating with DNSE Open API

## Product Development Requirements (PDR)

### Functional Requirements

#### FR-1: HTTP Client Operations (COMPLETE)
- Dual sync (`DnseClient`) and async (`AsyncDnseClient`) clients
- RESTful HTTP methods: GET, POST, PUT, DELETE, generic request()
- Context manager support for resource cleanup
- Configurable base URL and request timeout

#### FR-2: Authentication (COMPLETE)
- Bearer token authentication via Authorization header
- Optional API key parameter (empty string if not provided)
- Automatic header injection by HTTP config layer

#### FR-3: Error Handling (COMPLETE)
- Typed exception hierarchy: `DnseError` → `DnseAPIError` → (`DnseAuthError`, `DnseRateLimitError`)
- Automatic exception raising for non-2xx status codes
- Rate limit error includes retry-after seconds from headers
- Authentication errors for 401/403, API errors for others

#### FR-4: Response Models (COMPLETE)
- Pydantic v2 BaseModel (`DnseBaseModel`) with shared configuration
- Automatic snake_case ↔ camelCase conversion for JSON compatibility
- Type-safe data validation and serialization
- Extensible for domain-specific models

#### FR-5: Developer Experience (COMPLETE)
- Type hints throughout (strict pyright mode)
- Google-style docstrings for all public APIs
- Intuitive sync/async API consistency
- Clear error messages with context

### Non-Functional Requirements

#### NFR-1: Quality & Testing (COMPLETE)
- 28 comprehensive tests with 98% code coverage
- Unit tests for all client methods, exceptions, headers, models
- Integration-style tests with HTTP mocking (respx)
- Async test support (pytest-asyncio)
- All tests passing across Python 3.10/3.11/3.12

#### NFR-2: Type Safety (COMPLETE)
- Strict type checking (pyright strict mode)
- PEP 561 compliance (py.typed marker)
- Full type hints in all modules
- No untyped code or Any abuse

#### NFR-3: Code Quality (COMPLETE)
- Ruff linting: E, F, I, B, UP, D, S rules
- Google-style docstring convention
- Line length limit: 100 characters
- Pre-commit validation ready

#### NFR-4: Maintainability (COMPLETE)
- Clear module separation (HTTP, clients, models, exceptions)
- Reusable utilities in _http.py
- DRY principle applied (base model, shared headers)
- Documented TODOs for future API spec confirmation

#### NFR-5: Performance & Reliability (COMPLETE)
- Efficient httpx-based HTTP layer
- Connection pooling via httpx.Client
- Timeout handling (30s default, configurable)
- No memory leaks (proper client cleanup)

#### NFR-6: Release & Distribution (COMPLETE)
- Automated versioning via hatch-vcs + git tags
- GitHub Actions CI pipeline (lint → type → test matrix)
- PyPI publishing workflow automation
- Semantic versioning (0.1.0 initial release)

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

## Success Metrics (v0.1.0)

- [x] 98% code coverage achieved
- [x] Strict type checking passing
- [x] All linting rules satisfied
- [x] Tests passing on 3.10, 3.11, 3.12
- [x] CI pipeline green
- [x] Package buildable and publishable
- [x] Documentation complete
- [x] Exceptions properly typed and raised
- [x] Both sync and async clients working
- [x] Bearer token auth implemented

## Future Roadmap (v0.2+)

1. **Domain Models:** Add typed response models per API endpoint
2. **Retries & Backoff:** Automatic retry logic with exponential backoff
3. **Logging:** Structured logging for debugging
4. **Hooks/Middleware:** Request/response interceptors
5. **Streaming:** Support for streaming responses
6. **CLI:** Optional command-line interface for quick API calls

## Development Standards

See `/docs/code-standards.md` for implementation patterns, module organization, and contribution guidelines.

See `/docs/system-architecture.md` for deployment, integration, and infrastructure details.
