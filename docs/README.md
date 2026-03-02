# DNSE Python SDK Documentation

Welcome to the DNSE Python SDK documentation. This guide covers everything you need to know to use, develop, and contribute to the SDK.

## Documentation Structure

| Document | Purpose | Audience |
|----------|---------|----------|
| **[API Reference](./api-reference.md)** | Complete API documentation with examples | All users |
| **[Codebase Summary](./codebase-summary.md)** | Project structure and module overview | Developers |
| **[Project Overview & PDR](./project-overview-pdr.md)** | Requirements, architecture, and roadmap | Project leads, architects |
| **[Code Standards](./code-standards.md)** | Implementation patterns and conventions | Contributors |
| **[System Architecture](./system-architecture.md)** | Detailed technical architecture | Architects, advanced developers |

## Quick Navigation

### For Users
Start here if you're using the SDK:
1. **[API Reference](./api-reference.md)** - Complete API docs with examples
2. Check `/README.md` in project root for installation and quickstart

### For Contributors
Start here if you're contributing code:
1. **[Code Standards](./code-standards.md)** - Coding conventions and patterns
2. **[Codebase Summary](./codebase-summary.md)** - Project structure
3. **[System Architecture](./system-architecture.md)** - Module interactions

### For Architects & Leads
Start here for project decisions:
1. **[Project Overview & PDR](./project-overview-pdr.md)** - Requirements and roadmap
2. **[System Architecture](./system-architecture.md)** - Technical design
3. **[Code Standards](./code-standards.md)** - Quality benchmarks

## Key Information

### Project Summary
- **Name:** DNSE Python SDK
- **Version:** 0.1.0 (Foundation Complete)
- **Python:** 3.10+
- **Status:** Production-ready foundation
- **License:** MIT

### Core Features
- Sync and async HTTP clients (httpx-based)
- Typed exception hierarchy (DnseError, DnseAPIError, DnseAuthError, DnseRateLimitError)
- Pydantic v2 models with camelCase alias support
- 98% test coverage (28 comprehensive tests)
- Strict type checking (pyright strict mode)
- GitHub Actions CI/CD with test matrix (3.10/3.11/3.12)

### Quick Start

**Installation:**
```bash
pip install dnse
```

**Sync Usage:**
```python
from dnse import DnseClient

with DnseClient(api_key="your-api-key") as client:
    response = client.get("/v1/endpoint")
    data = response.json()
```

**Async Usage:**
```python
from dnse import AsyncDnseClient
import asyncio

async def main():
    async with AsyncDnseClient(api_key="your-api-key") as client:
        response = await client.get("/v1/endpoint")
        return response.json()

asyncio.run(main())
```

## Development Workflow

### Setup
```bash
uv sync              # Install dependencies
```

### Testing
```bash
uv run pytest                           # Run tests
uv run pytest --cov=src/dnse            # With coverage report
```

### Quality Checks
```bash
uv run ruff check .  # Lint check
uv run pyright       # Type check (strict)
```

### Building
```bash
uv build             # Build wheel + sdist
```

## Module Overview

### HTTP Clients
- **`DnseClient`** - Synchronous HTTP client with context manager support
- **`AsyncDnseClient`** - Asynchronous HTTP client for concurrent requests

### Exceptions
- **`DnseError`** - Base exception
- **`DnseAPIError`** - API returned error (status_code, body)
- **`DnseAuthError`** - Authentication failed (401/403)
- **`DnseRateLimitError`** - Rate limited (429, includes retry_after)

### Models
- **`DnseBaseModel`** - Pydantic v2 base with snake_case ↔ camelCase conversion

### HTTP Utilities (Private)
- **`HttpConfig`** - Immutable configuration dataclass
- **`build_headers()`** - Constructs request headers with auth
- **`handle_response()`** - Maps HTTP status codes to exceptions

## Code Quality Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Code Coverage | 95%+ | 98% |
| Type Coverage | 100% | 100% |
| Linting | No errors | ✓ Pass |
| Type Checking | Strict | ✓ Strict |
| Python 3.10 | ✓ | ✓ Pass |
| Python 3.11 | ✓ | ✓ Pass |
| Python 3.12 | ✓ | ✓ Pass |

## Architecture Highlights

### Layered Design
```
Application Code
     ↓
Client Layer (DnseClient, AsyncDnseClient)
     ↓
HTTP Utilities (_http.py)
     ↓
Exception Mapping
     ↓
Transport (httpx)
     ↓
DNSE API
```

### Error Handling
Automatic exception mapping based on HTTP status codes:
- 2xx → Success (return response)
- 401/403 → `DnseAuthError`
- 429 → `DnseRateLimitError` (with retry_after)
- Others → `DnseAPIError`

### Model Pattern
Pydantic v2 models support both naming conventions:
```python
class Order(DnseBaseModel):
    order_id: str
    total_amount: float

# Both work:
Order(order_id="123", total_amount=100.0)
Order(**{"orderId": "123", "totalAmount": 100.0})
```

## Known TODOs

1. **Confirm Base URL** - Currently `https://openapi.dnse.com.vn` (placeholder)
2. **Confirm Auth Format** - Bearer token assumed, needs API docs verification
3. **Add Domain Models** - Type-safe models per endpoint spec

## Contributing

1. Read [Code Standards](./code-standards.md) for conventions
2. Ensure tests pass: `uv run pytest`
3. Verify linting: `uv run ruff check .`
4. Check types: `uv run pyright`
5. Maintain 95%+ coverage
6. Follow Google-style docstrings

## Support & Resources

- **GitHub:** [dnse-tech/dnse-py](https://github.com/dnse-tech/dnse-py)
- **PyPI:** [dnse](https://pypi.org/project/dnse/)
- **Issues:** Report bugs and feature requests on GitHub
- **License:** MIT

## Version History

### v0.1.0 (Current)
- Foundation complete
- Sync and async clients
- Exception hierarchy
- Pydantic v2 models
- 98% test coverage
- GitHub Actions CI/CD
- Ready for production use

## Document Versions

- **Last Updated:** 2026-03-02
- **Format:** Markdown
- **Total Lines:** 1,213 (across 5 files)
- **Status:** Current and accurate

---

For detailed information, refer to specific documentation files above.
