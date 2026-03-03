# dnse

Python SDK for the DNSE Open API. Supports sync and async HTTP via `httpx`, HMAC-SHA256 authentication, Pydantic v2 response models, and strict typing.

## Installation

```bash
pip install dnse
```

## Quickstart

### Authentication

```python
from dnse import DnseClient

with DnseClient(api_key="your-api-key", api_secret="your-api-secret") as client:
    # Step 1: request OTP email
    client.registration.send_otp()

    # Step 2: verify OTP → sets trading token on client
    client.registration.verify_otp("123456")

    # Step 3: use resources
    accounts = client.accounts.list()
    orders = client.orders.list(accounts.accounts[0].id, marketType="STOCK")
```

### Resource API

```python
from dnse import DnseClient, PlaceOrderRequest

with DnseClient(api_key="k", api_secret="s") as client:
    # Accounts
    accts = client.accounts.list()
    balances = client.accounts.balances("0003979888")
    packages = client.accounts.loan_packages("0003979888")

    # Orders (trading token required for mutations)
    client.registration.verify_otp("123456")

    order = client.orders.place(PlaceOrderRequest(
        account_no="0003979888",
        symbol="HPG",
        side="NB",        # NB = buy, NS = sell
        order_type="LO",  # limit order
        quantity=100,
        price=27000.0,
    ))

    active = client.orders.list("0003979888", marketType="STOCK", orderCategory="NORMAL")
    history = client.orders.history("0003979888", **{"from": "2026-01-01", "to": "2026-03-01"})
    client.orders.cancel("0003979888", order.id or 0)

    # Deals
    deals = client.deals.list("0003979888")

    # Market
    sec = client.market.security_info("HPG")
    print(sec.ceiling_price, sec.floor_price)
```

### Async

```python
from dnse import AsyncDnseClient

async with AsyncDnseClient(api_key="k", api_secret="s") as client:
    await client.registration.verify_otp("123456")
    orders = await client.orders.list("0003979888", marketType="STOCK")
```

## Error Handling

```python
from dnse import DnseClient, DnseAuthError, DnseRateLimitError, DnseSessionExpiredError, DnseAPIError

with DnseClient(api_key="k", api_secret="s") as client:
    try:
        client.orders.list("0003979888")
    except DnseSessionExpiredError:
        # Trading token expired — re-verify OTP
        client.registration.verify_otp(input("OTP: "))
    except DnseAuthError:
        print("Authentication failed")
    except DnseRateLimitError as e:
        print(f"Rate limited. Retry after: {e.retry_after}s")
    except DnseAPIError as e:
        print(f"API error {e.status_code}: {e.body}")
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `api_key` | `""` | API key from DNSE portal |
| `api_secret` | `""` | API secret for HMAC signing |
| `base_url` | `https://openapi.dnse.com.vn` | API base URL |
| `timeout` | `30.0` | Request timeout (seconds) |
| `date_header` | `"date"` | Date header name (`"date"` or `"x-aux-date"`) |

## Development

```bash
uv sync
uv run pytest
uv run ruff check .
uv run pyright
```
