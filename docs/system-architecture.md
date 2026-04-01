# DNSE Python SDK - System Architecture

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│              Application Code (User)                     │
│  (Imports DnseClient, AsyncDnseClient, models)           │
└─────────────────────┬──────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│        Resource Layer (resources/)                      │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐   │
│  │Registration│  │   Accounts  │  │   Orders     │   │
│  │            │  │             │  │              │   │
│  │ send_otp() │  │  list()     │  │  place()     │   │
│  │verify_otp()│  │ balances()  │  │  list()      │   │
│  └────────────┘  │loan_packages│  │  get()       │   │
│                  │   ppse()    │  │  update()    │   │
│                  └─────────────┘  │  cancel()    │   │
│  ┌──────────────┐  ┌──────────┐  │  history()   │   │
│  │    Deals     │  │  Market  │  └──────────────┘   │
│  │             │  │          │                      │
│  │  list()     │  │security_ │                      │
│  └──────────────┘  │info()    │                      │
│                    └──────────┘                      │
└─────────────────────┬──────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│       Client Layer (client.py, async_client.py)        │
│  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │  DnseClient      │  │ AsyncDnseClient          │  │
│  │  (Sync)          │  │ (Async)                  │  │
│  │                  │  │                          │  │
│  │ @cached_property │  │ @cached_property         │  │
│  │ registration     │  │ registration             │  │
│  │ accounts, orders │  │ accounts, orders, ...    │  │
│  └──────────────────┘  └──────────────────────────┘  │
└─────────────────────┬──────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│       Base Client Layer (_base_client.py)              │
│  ┌────────────────────────────────────────────────┐   │
│  │  BaseClient                                    │   │
│  │  - Retry logic on 429 (up to 3 attempts)       │   │
│  │  - Typed response parsing (Pydantic validate)  │   │
│  │  - Trading token injection for order mutations │   │
│  │  - Session expiry detection (401 → check token)│   │
│  │  - Abstract _send() for sync/async             │   │
│  └────────────────────────────────────────────────┘   │
└─────────────────────┬──────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│    HMAC Signing Layer (_hmac_signer.py)                │
│  ┌────────────────────────────────────────────────┐   │
│  │  build_signature_headers()                     │   │
│  │  - HMAC-SHA256(api_secret, signature_string)   │   │
│  │  - Returns: x-api-key, X-Signature, Date/nonce│   │
│  │  - Nonce: uuid4().hex (32 char)                │   │
│  │  - Date: RFC 2822 format (configurable header) │   │
│  └────────────────────────────────────────────────┘   │
└─────────────────────┬──────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│    HTTP Utilities Layer (_http.py)                     │
│  ┌────────────────────────────────────────────────┐   │
│  │  HttpConfig (dataclass)                        │   │
│  │  - base_url, timeout, api_key, api_secret      │   │
│  │  - date_header ("date" or "x-aux-date")        │   │
│  └────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────┐   │
│  │  build_request_headers() → dict                │   │
│  │  - Calls build_signature_headers               │   │
│  │  - Injects trading-token if set and path match │   │
│  └────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────┐   │
│  │  handle_response()                             │   │
│  │  - 401 + trading_token → DnseSessionExpiredErr│   │
│  │  - 401/403 → DnseAuthError                     │   │
│  │  - 429 → DnseRateLimitError (retry_after)      │   │
│  └────────────────────────────────────────────────┘   │
└─────────────────────┬──────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│       Exception Layer (exceptions.py)                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  DnseError (base)                               │  │
│  │  └── DnseAPIError                               │  │
│  │      ├── DnseAuthError (401/403, no token)      │  │
│  │      ├── DnseSessionExpiredError (401, token)   │  │
│  │      └── DnseRateLimitError (429 + retry_after) │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────┬──────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────┐
│      Transport Layer (httpx)                           │
│  ┌──────────────┐  ┌────────────────────────────────┐ │
│  │ httpx.Client │  │ httpx.AsyncClient              │ │
│  │ (Connection  │  │ (Connection pool, async)       │ │
│  │  pool)       │  │                                │ │
│  └──────────────┘  └────────────────────────────────┘ │
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
- Clients: `DnseClient`, `AsyncDnseClient`
- Exceptions: `DnseError`, `DnseAPIError`, `DnseAuthError`, `DnseSessionExpiredError`, `DnseRateLimitError`
- Models: All domain models (`TwoFARequest`, `TwoFAResponse`, `AccountItem`, `OrderItem`, etc.)
- `__version__` - Package version from hatch-vcs

**Rule:** Only public, documented classes/functions in `__all__`

### 2. `_http.py` - HTTP Infrastructure (Private)
**Exports:**
- `HttpConfig` - Immutable configuration dataclass (api_key, api_secret, base_url, timeout, date_header)
- `build_request_headers()` - Header construction with HMAC + trading token injection
- `handle_response()` - HTTP status code to exception mapping
- `DEFAULT_BASE_URL` - API base URL constant

**Key Logic:**
```python
# Status mapping:
2xx → return (success)
401 + trading_token set → DnseSessionExpiredError
401/403 → DnseAuthError
429 → DnseRateLimitError (extracts retry-after)
others → DnseAPIError
```

### 3. `_base_client.py` - Base Client with Shared Logic
**Class:** `BaseClient`
**Methods:**
- `_request_headers(method, path)` - Build HMAC headers + inject trading token if needed
- `_parse(response, model)` - Typed Pydantic validation with handle_response
- `_should_retry(attempt, response)` - Backoff logic for 429
- `set_trading_token(token)` - Store token from OTP flow
- `request(method, path, **kwargs)` - Core retry loop + typed parsing
- `request_raw(method, path, **kwargs)` - Low-level, returns httpx.Response
- Abstract `_send(method, path, **kw)` - Implemented by sync/async clients

**Retry Logic:**
- MAX_RETRIES = 3, RETRY_BASE_DELAY = 1.0
- On 429: exponential backoff (2^attempt), respects retry-after header
- On other errors: immediate raise

### 4. `client.py` - Synchronous Client
**Class:** `DnseClient(BaseClient)`
**Interface:**
- `__init__(api_key, api_secret, base_url, timeout, date_header)`
- Thin I/O wrapper: `_send()` blocks on httpx
- Resource access: `@cached_property` for registration, accounts, orders, deals, market
- `close()`, context manager support

### 5. `async_client.py` - Asynchronous Client
**Class:** `AsyncDnseClient(BaseClient)`
**Interface:** Same as sync, fully async
- `_send()` is async, awaits httpx
- Same resource properties (async variants)
- `aclose()`, `async with` context manager

### 6. `_hmac_signer.py` - HMAC Signing
**Function:** `build_signature_headers(method, path, api_key, api_secret, date_header, use_nonce)`
**Returns:** dict with headers: `x-api-key`, `X-Signature`, `Date`/`X-Aux-Date`, optional `nonce`

**Signature Formula:**
```
signed_headers = "(request-target) date [nonce]"
sig_string = "(request-target): GET /path\ndate: Mon, 03 Mar 2026 12:00:00 +0000\n[nonce: {uuid}]"
signature = url_encode(base64(HMAC-SHA256(api_secret, sig_string)))
X-Signature: Signature keyId="{api_key}",algorithm="hmac-sha256",
  headers="(request-target) date [nonce]",signature="{sig}"[,nonce="{uuid}"]
```

### 7. `exceptions.py` - Exception Hierarchy
**Inheritance:**
```
Exception
└── DnseError
    └── DnseAPIError (base for API errors)
        ├── DnseAuthError (401/403, no trading token)
        ├── DnseSessionExpiredError (401 with trading token set)
        └── DnseRateLimitError (429 + retry_after)
```

**Attributes:**
- `DnseAPIError`: `status_code`, `body`
- `DnseRateLimitError`: `status_code`, `body`, `retry_after`
- `DnseSessionExpiredError`: inherits from DnseAuthError; signals token expired

### 8. `models/base.py` - Base Model
**Class:** `DnseBaseModel(pydantic.BaseModel)`
**Configuration:**
```python
model_config = ConfigDict(
    populate_by_name=True,        # Accept both naming styles
    alias_generator=to_camel,      # snake_case → camelCase
)
```

### 9. Domain Models (`models/{domain}.py`)
- `auth.py`: `TwoFARequest`, `TwoFAResponse`
- `accounts.py`: `AccountItem`, `AccountsResponse`, `BalanceItem`, `LoanPackage`, `PpseResponse`
- `orders.py`: `PlaceOrderRequest`, `PlaceOrderResponse`, `OrderItem`, `OrdersResponse`, `UpdateOrderRequest`, `OrderHistoryResponse`
- `deals.py`: `DealItem`, `DealsResponse`
- `market.py`: `SecurityDefinition`, `Trade`, `MarketResponse`

### 10. Resources (`resources/{domain}.py`)
- `registration.py`: `RegistrationResource`, `AsyncRegistrationResource`
- `accounts.py`: `AccountsResource`, `AsyncAccountsResource`
- `orders.py`: `OrdersResource`, `AsyncOrdersResource`
- `deals.py`: `DealsResource`, `AsyncDealsResource`
- `market.py`: `MarketResource`, `AsyncMarketResource`

Each resource class holds a reference to `BaseClient` and calls `client.request()` or `client.request_raw()`.

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
