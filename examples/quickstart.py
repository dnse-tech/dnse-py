"""Quickstart — full authentication flow and first API calls.

Setup:
  cp .env.example .env   # fill in credentials
  pip install "dnse[examples]"
  python quickstart.py

Debug mode (prints request headers and raw responses):
  DNSE_DEBUG=1 python quickstart.py
"""

from dotenv import load_dotenv

load_dotenv()

import logging  # noqa: E402
import os  # noqa: E402

from dnse import DnseClient  # noqa: E402
from dnse.models.accounts import AccountBalanceResponse  # noqa: E402

# Enable debug logging when DNSE_DEBUG=1
if os.environ.get("DNSE_DEBUG"):
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(name)s: %(message)s")
    # httpx request/response details (headers, status, body)
    logging.getLogger("httpx").setLevel(logging.DEBUG)
    logging.getLogger("httpcore").setLevel(logging.DEBUG)

API_KEY = os.environ["DNSE_API_KEY"]
API_SECRET = os.environ["DNSE_API_SECRET"]
BASE_URL = os.environ.get("DNSE_BASE_URL")  # optional — omit to use the default

# Print resolved config so credential issues are obvious immediately
print(f"[config] api_key={API_KEY[:6]}...  base_url={BASE_URL or 'default'}")

# Expected camelCase aliases for StockBalance fields
_STOCK_BALANCE_ALIASES = {
    "available_cash": "availableCash",
    "cash_dividend_receiving": "cashDividendReceiving",
    "deposit_fee_amount": "depositFeeAmount",
    "deposit_interest": "depositInterest",
    "total_cash": "totalCash",
    "total_debt": "totalDebt",
    "withdrawable_cash": "withdrawableCash",
}

kwargs = {"base_url": BASE_URL} if BASE_URL else {}
with DnseClient(api_key=API_KEY, api_secret=API_SECRET, **kwargs) as client:
    # --- Step 1: List accounts (no OTP needed) ---
    accounts = client.accounts.list()
    print(f"Investor: {accounts.investor_id}")
    for acct in accounts.accounts:
        print(
            f"  Account: {acct.id}  deal={acct.deal_account}  derivative={acct.derivative_account}"
        )

    # --- Step 2: Balances for first account ---
    acct_no = accounts.accounts[0].id

    # Fetch raw response to debug None fields before Pydantic parsing
    _path = f"/accounts/{acct_no}/balances"
    _headers = client._request_headers("GET", _path)
    _raw_resp = client._send("GET", _path, headers=_headers)
    _raw_json = _raw_resp.json()

    print(f"\n[DEBUG] Raw balances JSON: {_raw_json}")
    stock_raw = _raw_json.get("stock") or {}
    print(f"[DEBUG] Raw stock keys: {list(stock_raw.keys())}")
    for field, alias in _STOCK_BALANCE_ALIASES.items():
        raw_value = stock_raw.get(alias, "<KEY_MISSING>")
        print(f"[DEBUG]   {field} (alias={alias!r}): raw={raw_value!r}")

    balances = client._parse(_raw_resp, AccountBalanceResponse)
    print(f"\nBalances for {acct_no}:")
    print(f"  {balances}")

    # --- Step 3: Market data (no OTP needed) ---
    secs = client.market.security_info("HPG")
    sec = secs[0]  # server returns one entry per board; take first
    print(f"\nHPG — ceiling={sec.ceiling_price}  floor={sec.floor_price}")

    # --- Step 4 (optional): OTP for trading token ---
    # Uncomment to enable order/deal access:
    # otp = input("\nEnter OTP (or press Enter to skip): ").strip()
    # if otp:
    #     client.registration.verify_otp(otp)
    #     orders = client.orders.list(acct_no, marketType="STOCK")
    #     print(f"\nOpen orders: {len(orders.orders or [])}")
