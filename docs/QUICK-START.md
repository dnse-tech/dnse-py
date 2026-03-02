# DNSE Python SDK - Quick Start Guide

## Installation

```bash
pip install dnse
```

## Basic Usage (Sync)

```python
from dnse import DnseClient, DnseAuthError, DnseRateLimitError

with DnseClient(api_key="your-api-key") as client:
    try:
        response = client.get("/v1/endpoint")
        data = response.json()
        print(data)
    except DnseAuthError:
        print("Authentication failed")
    except DnseRateLimitError as e:
        print(f"Rate limited. Retry after {e.retry_after}s")
```

## Basic Usage (Async)

```python
import asyncio
from dnse import AsyncDnseClient

async def main():
    async with AsyncDnseClient(api_key="your-api-key") as client:
        response = await client.get("/v1/endpoint")
        data = response.json()
        print(data)

asyncio.run(main())
```

## Working with Models

```python
from dnse.models import DnseBaseModel

class User(DnseBaseModel):
    user_id: str
    created_at: str
    is_active: bool

# Parse API response
user = User(**response.json())
print(user.user_id)
```

## Environment Variables

```python
import os
from dnse import DnseClient

api_key = os.getenv("DNSE_API_KEY")
with DnseClient(api_key=api_key) as client:
    response = client.get("/v1/endpoint")
```

## Error Handling

```python
from dnse import (
    DnseClient,
    DnseError,
    DnseAuthError,
    DnseRateLimitError,
    DnseAPIError
)

with DnseClient(api_key="key") as client:
    try:
        response = client.post("/v1/orders", json={"item": "value"})
    except DnseAuthError as e:
        # 401 or 403
        print(f"Auth error: {e.status_code}")
    except DnseRateLimitError as e:
        # 429 with retry-after
        wait = e.retry_after or 60
        print(f"Rate limited, wait {wait}s")
    except DnseAPIError as e:
        # Other non-2xx responses
        print(f"API error {e.status_code}: {e.body}")
    except DnseError as e:
        # Catch-all for SDK errors
        print(f"DNSE error: {e}")
```

## Configuration Options

```python
from dnse import DnseClient

client = DnseClient(
    api_key="your-api-key",
    base_url="https://api.dnse.com.vn",  # Override default
    timeout=60.0                          # Custom timeout
)
```

## Common Patterns

### Retry with Backoff
```python
import time
from dnse import DnseClient, DnseRateLimitError

with DnseClient(api_key="key") as client:
    for attempt in range(3):
        try:
            return client.get("/v1/endpoint")
        except DnseRateLimitError as e:
            if attempt < 2:
                wait = e.retry_after or (2 ** attempt)
                print(f"Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
```

### Async Concurrent Requests
```python
import asyncio
from dnse import AsyncDnseClient

async def fetch_all(endpoints):
    async with AsyncDnseClient(api_key="key") as client:
        tasks = [client.get(ep) for ep in endpoints]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]

results = asyncio.run(fetch_all(["/v1/users", "/v1/orders"]))
```

### POST Request with JSON
```python
from dnse import DnseClient

with DnseClient(api_key="key") as client:
    response = client.post(
        "/v1/orders",
        json={
            "customer_id": "123",
            "items": [{"product_id": "abc", "quantity": 2}]
        }
    )
    order = response.json()
```

### Custom Headers
```python
from dnse import DnseClient

with DnseClient(api_key="key") as client:
    response = client.get(
        "/v1/endpoint",
        headers={"X-Custom-Header": "value"}
    )
```

## Troubleshooting

### Import Error
```python
# Make sure dnse is installed
# pip install dnse

from dnse import DnseClient
```

### 401/403 Authentication Error
```python
# Check API key
# Ensure it's valid and hasn't expired
# Use environment variable instead of hardcoding

import os
api_key = os.getenv("DNSE_API_KEY")
if not api_key:
    raise ValueError("DNSE_API_KEY environment variable not set")
```

### 429 Rate Limit
```python
# Implement exponential backoff with retry-after
from dnse import DnseRateLimitError

try:
    response = client.get("/v1/endpoint")
except DnseRateLimitError as e:
    wait = e.retry_after or 60
    # Implement backoff
```

### Timeout Errors
```python
# Increase timeout for slow endpoints
client = DnseClient(api_key="key", timeout=120.0)
```

## Next Steps

1. **Read Full API Reference:** `/docs/api-reference.md`
2. **Explore Architecture:** `/docs/system-architecture.md`
3. **See Examples:** Check the `examples/` directory (if available)
4. **Report Issues:** GitHub Issues page

## Documentation Map

| Need | Reference |
|------|-----------|
| API Methods & Exceptions | [api-reference.md](./api-reference.md) |
| Project Overview | [codebase-summary.md](./codebase-summary.md) |
| Code Conventions | [code-standards.md](./code-standards.md) |
| Technical Design | [system-architecture.md](./system-architecture.md) |
| Requirements & Roadmap | [project-overview-pdr.md](./project-overview-pdr.md) |
| Full Documentation Index | [README.md](./README.md) |

## Version

```python
from dnse import __version__
print(__version__)  # e.g., "0.1.0"
```

## Support

- **GitHub:** https://github.com/dnse-tech/dnse-py
- **Issues:** Report bugs and feature requests
- **PyPI:** https://pypi.org/project/dnse/
