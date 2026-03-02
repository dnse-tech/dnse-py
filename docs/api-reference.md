# DNSE Python SDK - API Reference

## Quick Start

### Installation
```bash
pip install dnse
```

### Sync Usage
```python
from dnse import DnseClient, DnseAuthError, DnseRateLimitError

with DnseClient(api_key="your-api-key") as client:
    try:
        response = client.get("/v1/endpoint")
        data = response.json()
    except DnseAuthError:
        print("Auth failed")
    except DnseRateLimitError as e:
        print(f"Rate limited, retry after {e.retry_after}s")
```

### Async Usage
```python
import asyncio
from dnse import AsyncDnseClient

async def main():
    async with AsyncDnseClient(api_key="your-api-key") as client:
        response = await client.get("/v1/endpoint")
        data = response.json()

asyncio.run(main())
```

## Client API

### DnseClient (Sync)

```python
class DnseClient:
    def __init__(
        self,
        api_key: str = "",
        *,
        base_url: str = "https://openapi.dnse.com.vn",
        timeout: float = 30.0,
    ) -> None:
        """Initialize sync DNSE client.

        Args:
            api_key: Bearer token for authentication.
            base_url: API base URL (default: https://openapi.dnse.com.vn).
            timeout: Request timeout in seconds (default: 30.0).
        """

    def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Send HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            path: URL path relative to base_url.
            **kwargs: Additional arguments passed to httpx.Client.request().

        Returns:
            httpx.Response object.

        Raises:
            DnseAuthError: On 401 or 403 response.
            DnseRateLimitError: On 429 response.
            DnseAPIError: On other non-2xx responses.
        """

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send GET request."""

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send POST request."""

    def put(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send PUT request."""

    def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send DELETE request."""

    def close(self) -> None:
        """Close underlying HTTP client."""

    def __enter__(self) -> DnseClient:
        """Enter context manager."""

    def __exit__(self, *args: object) -> None:
        """Exit context manager and close client."""
```

### AsyncDnseClient (Async)

```python
class AsyncDnseClient:
    # Same interface as DnseClient, but all methods are async:

    async def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Send HTTP request (async)."""

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send GET request (async)."""

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send POST request (async)."""

    async def put(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send PUT request (async)."""

    async def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        """Send DELETE request (async)."""

    async def close(self) -> None:
        """Close underlying HTTP client."""

    async def __aenter__(self) -> AsyncDnseClient:
        """Enter async context manager."""

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager and close client."""
```

## Exceptions

### DnseError
Base exception for all DNSE SDK errors.

```python
try:
    # ...
except DnseError as e:
    print(f"DNSE error: {e}")
```

### DnseAPIError
API returned an error response. Parent class for specific errors.

**Attributes:**
- `status_code: int` - HTTP status code
- `body: str` - Response body text

```python
try:
    client.get("/v1/endpoint")
except DnseAPIError as e:
    print(f"Error {e.status_code}: {e.body}")
```

### DnseAuthError
Authentication failed (401 or 403).

Inherits from `DnseAPIError`, so has `status_code` and `body`.

```python
try:
    client.get("/v1/protected")
except DnseAuthError as e:
    print(f"Auth failed: {e.status_code}")
```

### DnseRateLimitError
Rate limit exceeded (429).

**Attributes:**
- `status_code: int` - Always 429
- `body: str` - Response body
- `retry_after: float | None` - Seconds to wait before retry (from Retry-After header)

```python
import asyncio

try:
    client.get("/v1/endpoint")
except DnseRateLimitError as e:
    wait_time = e.retry_after or 60.0
    print(f"Rate limited, retrying in {wait_time}s")
    asyncio.sleep(wait_time)
```

## Models

### DnseBaseModel
Base Pydantic v2 model for response data.

**Features:**
- Automatic snake_case ↔ camelCase conversion
- Full Pydantic validation
- Both naming styles accepted

```python
from dnse.models import DnseBaseModel

class User(DnseBaseModel):
    user_id: str
    created_at: str
    is_active: bool

# From JSON response (camelCase):
user = User(**{"userId": "123", "createdAt": "2025-03-02", "isActive": true})

# From Python kwargs (snake_case):
user = User(user_id="123", created_at="2025-03-02", is_active=True)

# Access fields:
print(user.user_id)
print(user.created_at)

# Serialize back to camelCase:
print(user.model_dump(by_alias=True))
# {'userId': '123', 'createdAt': '2025-03-02', 'isActive': True}
```

## Common Patterns

### Error Handling with Retries
```python
import time
from dnse import DnseClient, DnseRateLimitError

with DnseClient(api_key="key") as client:
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return client.get("/v1/endpoint")
        except DnseRateLimitError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = e.retry_after or (2 ** attempt)
            print(f"Rate limited, waiting {wait_time}s")
            time.sleep(wait_time)
```

### Parsing Responses with Models
```python
from dnse import DnseClient
from dnse.models import DnseBaseModel

class Order(DnseBaseModel):
    order_id: str
    total_amount: float
    status: str

with DnseClient(api_key="key") as client:
    response = client.get("/v1/orders/123")
    order = Order(**response.json())
    print(f"Order {order.order_id}: {order.status}")
```

### Async Multiple Requests
```python
import asyncio
from dnse import AsyncDnseClient

async def fetch_multiple(endpoints: list[str]) -> list:
    async with AsyncDnseClient(api_key="key") as client:
        tasks = [client.get(ep) for ep in endpoints]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]

results = asyncio.run(fetch_multiple(["/v1/users", "/v1/orders"]))
```

### Custom Request Parameters
```python
from dnse import DnseClient

with DnseClient(api_key="key") as client:
    # Pass kwargs to httpx (headers, params, json, etc.)
    response = client.post(
        "/v1/orders",
        json={"items": [{"id": "1", "qty": 2}]},
        headers={"X-Custom": "value"},
        params={"dry_run": "true"},
    )
```

## Version Information

```python
from dnse import __version__

print(__version__)  # e.g., "0.1.0"
```

## Environment Variables

Recommended for API key management:

```python
import os
from dnse import DnseClient

api_key = os.getenv("DNSE_API_KEY")
with DnseClient(api_key=api_key) as client:
    # ...
```

## Request Timeout

Customize timeout per client:

```python
from dnse import DnseClient

# 60 second timeout
client = DnseClient(api_key="key", timeout=60.0)

# Short timeout for health checks
quick_client = DnseClient(api_key="key", timeout=5.0)
```

## Base URL Configuration

Override for testing or alternative deployments:

```python
from dnse import DnseClient

# Custom base URL
client = DnseClient(
    api_key="key",
    base_url="https://staging-api.dnse.com.vn"
)
```

## Response Object

The `response` returned by all request methods is an `httpx.Response`:

```python
response = client.get("/v1/endpoint")

# Common methods/properties:
response.status_code        # int (e.g., 200)
response.headers            # dict-like
response.text               # str
response.content            # bytes
response.json()             # dict/list (parsed JSON)
response.is_success         # bool (200-299)
response.raise_for_status() # Raise on 4xx/5xx
```

See [httpx documentation](https://www.python-httpx.org/) for full API.
