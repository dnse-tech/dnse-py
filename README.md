# dnse

Python SDK for the DNSE Open API. Supports sync and async HTTP via `httpx`, Pydantic v2 response models, and strict typing.

## Installation

```bash
pip install dnse
```

## Quickstart

### Sync

```python
from dnse import DnseClient

with DnseClient(api_key="your-api-key") as client:
    response = client.get("/v1/some-endpoint")
    data = response.json()
```

### Async

```python
from dnse import AsyncDnseClient

async with AsyncDnseClient(api_key="your-api-key") as client:
    response = await client.get("/v1/some-endpoint")
    data = response.json()
```

## Error Handling

```python
from dnse import DnseClient, DnseAuthError, DnseRateLimitError, DnseAPIError

with DnseClient(api_key="your-api-key") as client:
    try:
        response = client.get("/v1/some-endpoint")
    except DnseAuthError:
        print("Authentication failed")
    except DnseRateLimitError as e:
        print(f"Rate limited. Retry after: {e.retry_after}s")
    except DnseAPIError as e:
        print(f"API error {e.status_code}: {e.body}")
```

## Development

```bash
uv sync
uv run pytest
uv run ruff check .
uv run pyright
```

> **Note:** Base URL and authentication details are placeholders pending official DNSE Open API documentation.
