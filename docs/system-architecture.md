# DNSE Python SDK - System Architecture

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│              Application Code (User)                     │
│  (Imports DnseClient, AsyncDnseClient, exceptions)       │
└─────────────────────┬──────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│          Client Layer (client.py, async_client.py)      │
│  ┌──────────────────┐  ┌──────────────────────────┐   │
│  │  DnseClient      │  │  AsyncDnseClient         │   │
│  │  (Sync)          │  │  (Async)                 │   │
│  └──────────────────┘  └──────────────────────────┘   │
│  - Context managers                                    │
│  - Request routing (GET, POST, PUT, DELETE)            │
│  - Response error handling                             │
└─────────────────────┬──────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│          HTTP Utilities Layer (_http.py)               │
│  ┌──────────────────────────────────────────────┐    │
│  │  HttpConfig (dataclass)                      │    │
│  │  - base_url (default: openapi.dnse.com.vn)   │    │
│  │  - timeout (default: 30.0s)                  │    │
│  │  - api_key (Bearer token)                    │    │
│  └──────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────┐    │
│  │  build_headers(config) → dict[str, str]      │    │
│  │  - User-Agent, Accept                        │    │
│  │  - Authorization (if api_key set)            │    │
│  └──────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────┐    │
│  │  handle_response(status, body, headers)      │    │
│  │  - Maps HTTP codes to typed exceptions       │    │
│  │  - Extracts retry-after from headers         │    │
│  └──────────────────────────────────────────────┘    │
└─────────────────────┬──────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│       Exception Layer (exceptions.py)                   │
│  ┌──────────────────┐                                 │
│  │  DnseError       │ (Base)                          │
│  └────────┬─────────┘                                 │
│           │                                           │
│  ┌────────▼──────────────┐                           │
│  │  DnseAPIError         │ (status_code, body)       │
│  └────────┬──────────────┘                           │
│           │                                           │
│     ┌─────┴──────┬──────────────────┐               │
│     │            │                  │               │
│  ┌──▼──┐  ┌──────▼──────┐  ┌────────▼────┐        │
│  │401/ │  │   429       │  │  Other      │        │
│  │403  │  │  (Rate Lim) │  │  (Generic)  │        │
│  └─────┘  └─────────────┘  └─────────────┘        │
│  DnseAuthError  DnseRateLimitError   DnseAPIError │
└──────────────────────────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│       Model Layer (models/base.py)                      │
│  ┌────────────────────────────────────────────────┐   │
│  │  DnseBaseModel (Pydantic v2 BaseModel)         │   │
│  │  - populate_by_name=True                       │   │
│  │  - alias_generator=to_camel                    │   │
│  │  - Serialization: snake_case ↔ camelCase      │   │
│  └────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│      Transport Layer (httpx)                           │
│  ┌──────────────┐  ┌────────────────────────────────┐│
│  │ httpx.Client │  │ httpx.AsyncClient              ││
│  │ (Connection  │  │ (Connection pool, async)       ││
│  │  pool)       │  │                                ││
│  └──────────────┘  └────────────────────────────────┘│
└─────────────────────┬──────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│      Network Layer                                      │
│  DNSE Open API (https://openapi.dnse.com.vn)          │
└──────────────────────────────────────────────────────┘
```

## Module Responsibilities

### 1. `__init__.py` - Public API Gateway
**Exports:**
- `DnseClient`, `AsyncDnseClient` - Client classes
- `DnseError`, `DnseAPIError`, `DnseAuthError`, `DnseRateLimitError` - Exceptions
- `__version__` - Package version from hatch-vcs

**Rule:** Only public, documented classes/functions in `__all__`

### 2. `_http.py` - HTTP Infrastructure (Private)
**Exports:**
- `HttpConfig` - Immutable configuration dataclass
- `build_headers()` - Header construction with auth
- `handle_response()` - HTTP status code to exception mapping
- `DEFAULT_BASE_URL` - API base URL constant

**Key Logic:**
```python
# Status mapping:
2xx → return (success)
401/403 → DnseAuthError
429 → DnseRateLimitError (extracts retry-after)
others → DnseAPIError
```

### 3. `client.py` - Synchronous Client
**Class:** `DnseClient`
**Interface:**
- `__init__(api_key, base_url, timeout)` - Initialize
- `request(method, path, **kwargs)` - Core method
- `get()`, `post()`, `put()`, `delete()` - Convenience methods
- `close()` - Manual cleanup
- Context manager (`__enter__`, `__exit__`)

**Flow:**
1. User calls `client.get(path)`
2. Routes to `request("GET", path)`
3. Calls `self._client.request()` (httpx)
4. Calls `handle_response()` (may raise exception)
5. Returns `httpx.Response` on success

### 4. `async_client.py` - Asynchronous Client
**Class:** `AsyncDnseClient`
**Interface:** Identical to `DnseClient` but all methods are async
**Key Differences:**
- Uses `httpx.AsyncClient`
- All methods are coroutines
- Works with `async with` context manager
- Use `await client.get(path)`

### 5. `exceptions.py` - Exception Hierarchy
**Inheritance:**
```
Exception
└── DnseError
    └── DnseAPIError (base for API errors)
        ├── DnseAuthError (401/403)
        └── DnseRateLimitError (429)
```

**Attributes:**
- `DnseAPIError`: `status_code`, `body`
- `DnseRateLimitError`: `status_code`, `body`, `retry_after`

### 6. `models/base.py` - Base Model
**Class:** `DnseBaseModel(pydantic.BaseModel)`
**Configuration:**
```python
model_config = ConfigDict(
    populate_by_name=True,        # Accept both naming styles
    alias_generator=to_camel,      # snake_case → camelCase
)
```

**Usage:**
```python
class User(DnseBaseModel):
    user_id: str
    created_at: str

# Both work:
User(user_id="123", created_at="2025-03-02")
User(**{"userId": "123", "createdAt": "2025-03-02"})
```

## Data Flow Example

### Sync Request with Error Handling
```
User Code
  │
  ├─ with DnseClient(api_key="abc") as client:
  │       response = client.get("/v1/users")
  │
  ├─ DnseClient.__init__
  │   └─ HttpConfig(base_url, timeout, api_key="abc")
  │   └─ httpx.Client with headers: {Authorization: Bearer abc}
  │
  ├─ DnseClient.get("/v1/users")
  │   └─ request("GET", "/v1/users")
  │
  ├─ self._client.request("GET", "/v1/users")
  │   └─ httpx makes network call
  │   └─ returns httpx.Response (status=200, body=JSON)
  │
  ├─ handle_response(200, body, headers)
  │   └─ 200 in range(200, 300) → return (success)
  │
  └─ User receives httpx.Response
      └─ response.json() → parsed data
      └─ Optional: data = User(**response.json())
```

### Error Scenario (Rate Limited)
```
httpx returns 429 response
  │
  ├─ handle_response(429, "Too many requests", {"retry-after": "60"})
  │   └─ retry_after = float(headers["retry-after"]) = 60.0
  │   └─ raise DnseRateLimitError(429, "Too many requests", 60.0)
  │
  └─ User's except block
      ├─ except DnseRateLimitError as e:
      │   └─ e.status_code = 429
      │   └─ e.body = "Too many requests"
      │   └─ e.retry_after = 60.0
      │   └─ User can sleep/backoff
```

## Integration Points

### Adding a New Endpoint Model
1. Create model in `src/dnse/models/{domain}.py`
2. Inherit from `DnseBaseModel`
3. Add type hints for all fields
4. Export from `models/__init__.py`
5. Write tests in `tests/test_{domain}_models.py`

### Adding a New Client Method
1. Add method to both `DnseClient` and `AsyncDnseClient`
2. Use `self.request()` or `await self.request()`
3. Document with docstring (Args, Returns, Raises)
4. Write tests using `respx_mock` for HTTP mocking
5. Ensure coverage remains ≥95%

## Testing Architecture

**Test Layers:**
1. **Unit Tests** - Individual functions/methods
2. **Integration Tests** - Client + HTTP mocking (respx)
3. **Model Tests** - Pydantic serialization/deserialization
4. **Exception Tests** - Error handling scenarios

**Mocking Strategy:**
```python
def test_auth_error(respx_mock):
    # Mock HTTP response
    respx_mock.get("https://openapi.dnse.com.vn/v1/users").mock(
        return_value=httpx.Response(401, text="Invalid token")
    )

    # Test client behavior
    with DnseClient(api_key="bad") as client:
        with pytest.raises(DnseAuthError) as exc_info:
            client.get("/v1/users")

        assert exc_info.value.status_code == 401
```

## Deployment & Distribution

### Build Process (hatchling)
1. Read git tag (hatch-vcs)
2. Auto-generate `src/dnse/_version.py`
3. Wheel + sdist build
4. Publish to PyPI

### CI/CD Pipeline (GitHub Actions)
1. **Lint:** ruff check (100 char lines, Google docstrings)
2. **Type Check:** pyright strict mode
3. **Test:** pytest on Python 3.10, 3.11, 3.12 with respx mocking
4. **Release:** Auto-publish on git tags

### Version Management
- Source: git tags (e.g., `v0.1.0`)
- Auto-populated: `src/dnse/_version.py` at build time
- Retrieved: `from dnse import __version__`

## Performance Characteristics

| Aspect | Details |
|--------|---------|
| **Sync Latency** | Network RTT + API processing |
| **Async Latency** | Same, but can handle multiple concurrent |
| **Connection Pooling** | httpx.Client maintains TCP pool |
| **Timeout** | 30s default (configurable) |
| **Memory** | ~200KB per idle client + connection state |
| **Throughput** | Limited by DNSE API rate limits (429 handling) |

## Security Architecture

1. **Authentication:** Bearer token in `Authorization: Bearer {api_key}`
2. **Transport:** HTTPS only
3. **Input Validation:** Pydantic validates all model data
4. **Type Safety:** Strict typing prevents injection
5. **Error Messages:** Do not log sensitive data
6. **Secrets Management:** Use environment variables, never hardcode

## Future Extension Points

1. **Middleware/Hooks:** Add request/response interceptors
2. **Retries:** Automatic exponential backoff for rate limits
3. **Logging:** Structured logging with DEBUG level support
4. **Streaming:** Support for streaming response bodies
5. **Batch Operations:** Helper for bulk API calls
