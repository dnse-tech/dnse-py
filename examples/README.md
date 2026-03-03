# dnse-py Examples

Runnable sample code covering all major SDK capabilities.

## Prerequisites

- Python 3.10+
- A DNSE API key and secret from [openapi.dnse.com.vn](https://openapi.dnse.com.vn)

## Install

```bash
pip install "dnse[examples]"
# or: pip install dnse python-dotenv
```

## Configure

```bash
cp .env.example .env
# Edit .env and fill in your credentials
```

## Run

```bash
python quickstart.py               # recommended starting point
python use-cases/portfolio-check.py
python use-cases/market-data.py
```

## File Guide

| File | Demonstrates | OTP? |
|------|-------------|------|
| `quickstart.py` | Auth flow, accounts, balances, market data | No |
| `use-cases/portfolio-check.py` | List accounts + balances | No |
| `use-cases/order-history.py` | Historical orders + today's deals | No |
| `use-cases/market-data.py` | Price limits for a list of symbols | No |
| `use-cases/place-a-trade.py` | OTP → buy order → cancel (**real order**) | Yes |
| `reference/accounts.py` | All `AccountsResource` methods | No |
| `reference/orders.py` | All `OrdersResource` methods | Optional |
| `reference/deals.py` | `DealsResource.list()` | No |
| `reference/market.py` | `MarketResource.security_info()` + `BoardId` enum filter | No |
| `reference/market-stream.py` | `DnseMarketStream` — trades, quotes, ohlc | No |
| `reference/trading-stream.py` | `DnseTradingStream` — orders, positions | No |
| `reference/async-client.py` | `AsyncDnseClient` pattern | No |

> **Note:** `use-cases/place-a-trade.py` places a **real limit order** on your account. It uses a price well below market to prevent it from filling, and cancels the order at the end.
