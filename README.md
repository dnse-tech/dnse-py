# dnse

Python SDK for the DNSE Open API. Supports sync and async HTTP via `httpx`, WebSocket streaming, HMAC-SHA256 authentication, Pydantic v2 response models, and strict typing.

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
    orders = client.orders.list(accounts.accounts[0].id, market_type="STOCK", order_category="NORMAL")
```

### Resource API

```python
from dnse import BoardId, DnseClient, PlaceOrderRequest, UpdateOrderRequest

with DnseClient(api_key="k", api_secret="s") as client:
    # Accounts
    accts = client.accounts.list()
    balances = client.accounts.balances("0003979888")
    packages = client.accounts.loan_packages("0003979888", market_type="STOCK", symbol="HPG")
    ppse = client.accounts.ppse("0003979888", market_type="STOCK")

    # Orders (trading token required for mutations)
    client.registration.verify_otp("123456")

    # Get security info for valid price range
    secs = client.market.security_info("HPG", board_id=BoardId.ROUND_LOT)
    sec = secs[0]
    print(sec.ceiling_price, sec.floor_price)

    order = client.orders.place(PlaceOrderRequest(
        account_no="0003979888",
        symbol="HPG",
        side="NB",        # NB = buy, NS = sell
        order_type="LO",  # limit order
        quantity=100,
        price=sec.floor_price,
    ))

    detail = client.orders.get("0003979888", order.id or 0)
    active = client.orders.list("0003979888", market_type="STOCK", order_category="NORMAL")
    history = client.orders.history("0003979888", **{"from": "2026-01-01", "to": "2026-03-01"})

    # Update (cancel-then-replace) — returned id is the NEW order id
    updated = client.orders.update("0003979888", order.id or 0, UpdateOrderRequest(
        price=sec.ceiling_price,
        quantity=100,
    ))

    client.orders.cancel("0003979888", order.id or 0)

    # Deals
    deals = client.deals.list("0003979888", market_type="STOCK")
```

### Async

```python
from dnse import AsyncDnseClient

async with AsyncDnseClient(api_key="k", api_secret="s") as client:
    await client.registration.verify_otp("123456")
    orders = await client.orders.list("0003979888", market_type="STOCK", order_category="NORMAL")
```

### WebSocket Streaming

#### Market Data

```python
from dnse import DnseMarketStream

stream = DnseMarketStream(api_key="k", api_secret="s")

async def on_trade(msg):
    print(msg.symbol, msg.price, msg.volume)

async def on_quote(msg):
    print(msg.bid_price, msg.ask_price)

async def on_ohlc(msg):
    print(msg.open, msg.high, msg.low, msg.close)

async def on_expected_price(msg):
    print(msg.price)

async def on_secdef(msg):
    print(msg.ceiling, msg.floor, msg.ref_price)

stream.subscribe_trades(["HPG", "VIC"], on_trade)
stream.subscribe_quotes(["HPG"], on_quote)
stream.subscribe_ohlc(["HPG"], on_ohlc, timeframe="1m")
stream.subscribe_expected_price(["HPG"], on_expected_price)
stream.subscribe_security_def(["HPG"], on_secdef)

stream.run()  # blocking; call from a thread or wrap with asyncio.to_thread
```

#### Trading Events (private)

```python
from dnse import DnseTradingStream

stream = DnseTradingStream(api_key="k", api_secret="s")

async def on_order(msg):
    print(msg.order_id, msg.status)

async def on_position(msg):
    print(msg.symbol, msg.qty, msg.avg_price)

async def on_account(msg):
    print(msg.account_no, msg.balance, msg.equity)

stream.subscribe_orders(on_order)
stream.subscribe_positions(on_position)
stream.subscribe_account(on_account)

stream.run()
```

## Error Handling

```python
from dnse import DnseClient, DnseAuthError, DnseRateLimitError, DnseSessionExpiredError, DnseAPIError
from dnse.stream.exceptions import DnseStreamError, DnseStreamAuthError, DnseStreamConnectionError

with DnseClient(api_key="k", api_secret="s") as client:
    try:
        client.orders.list("0003979888", market_type="STOCK", order_category="NORMAL")
    except DnseSessionExpiredError:
        # Trading token expired — re-verify OTP
        client.registration.verify_otp(input("OTP: "))
    except DnseAuthError:
        print("Authentication failed")
    except DnseRateLimitError as e:
        print(f"Rate limited. Retry after: {e.retry_after}s")
        if e.rate_limit_info:
            print(f"Remaining: {e.rate_limit_info.remaining}/{e.rate_limit_info.limit}")
    except DnseAPIError as e:
        print(f"API error {e.status_code}: {e.body}")
```

## Rate Limiting

### Catching 429 errors

```python
from dnse import DnseClient, DnseRateLimitError

with DnseClient(api_key="k", api_secret="s") as client:
    try:
        client.accounts.list()
    except DnseRateLimitError as e:
        info = e.rate_limit_info
        if info:
            print(f"Limit: {info.limit}, Remaining: {info.remaining}")
            print(f"Resets in {info.seconds_until_reset:.0f}s")
```

### Proactive quota checking

```python
from dnse import DnseClient, parse_rate_limit_info

with DnseClient(api_key="k", api_secret="s") as client:
    response = client.get("/accounts")
    info = parse_rate_limit_info(dict(response.headers))
    if info and info.remaining is not None and info.remaining < 10:
        print("Running low on API quota")
```

## OTP Methods

`verify_otp` accepts an `otp_type` keyword to select the OTP delivery method:

```python
client.registration.verify_otp("123456", otp_type="email_otp")   # default
client.registration.verify_otp("123456", otp_type="smart_otp")
```

## Stream Message Models

| Type field | Model class | Description |
|-----------|-------------|-------------|
| `"t"` | `StreamTrade` | Trade tick (price, volume, side) |
| `"te"` | `StreamTradeExtra` | Trade tick with cumulative total |
| `"q"` | `StreamQuote` | Best bid/ask quote |
| `"b"` | `StreamOhlc` | OHLC candlestick bar |
| `"e"` | `StreamExpectedPrice` | Expected/reference price |
| `"sd"` | `StreamSecurityDef` | Security definition with price limits |
| `"o"` | `StreamOrder` | Order update (private) |
| `"p"` | `StreamPosition` | Position update (private) |
| `"a"` | `StreamAccountUpdate` | Account balance update (private) |

## Market Enums

```python
from dnse.models.market import BoardId, MarketId, ProductGrpId, SecurityGroupId, SecurityStatus
```

Use these for type-safe filtering of `SecurityDefinition` fields returned by `client.market.security_info()`.

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
