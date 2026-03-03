"""Market Data — security info and price limits for a list of symbols.

No OTP required.

Setup: cp .env.example .env → fill credentials → pip install "dnse[examples]"
Run:   python use-cases/market-data.py
"""

from dotenv import load_dotenv

load_dotenv()

import os  # noqa: E402

from dnse import DnseClient  # noqa: E402

SYMBOLS = ["HPG", "VIC", "VNM", "SSI", "TCB"]

with DnseClient(
    api_key=os.environ["DNSE_API_KEY"], api_secret=os.environ["DNSE_API_SECRET"]
) as client:
    print(f"{'Symbol':<8} {'Ceiling':>10} {'Floor':>10} {'Ref':>10}")
    print("-" * 42)
    for sym in SYMBOLS:
        sec = client.market.security_info(sym)[0]  # first board entry
        print(f"{sym:<8} {sec.ceiling_price:>10} {sec.floor_price:>10} {sec.basic_price:>10}")
