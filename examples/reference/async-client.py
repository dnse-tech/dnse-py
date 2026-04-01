"""Reference: AsyncDnseClient — async variant for all resources.

No OTP required for read calls shown here.

Run: python reference/async-client.py
"""

from dotenv import load_dotenv

load_dotenv()

import asyncio  # noqa: E402
import os  # noqa: E402

from dnse import AsyncDnseClient  # noqa: E402

ACCOUNT_NO = os.environ["DNSE_ACCOUNT_NO"]


async def main():
    """Run async client examples."""
    async with AsyncDnseClient(
        api_key=os.environ["DNSE_API_KEY"],
        api_secret=os.environ["DNSE_API_SECRET"],
    ) as client:
        # Accounts
        accounts = await client.accounts.list()
        print("accounts:", accounts.investor_id)

        balances = await client.accounts.balances(ACCOUNT_NO)
        print("balances:", balances)

        # Market
        from dnse import BoardId  # noqa: E402

        secs = await client.market.security_info("HPG")
        sec = secs[0]
        print("security_info:", sec.ceiling_price, sec.floor_price)

        trades = await client.market.latest_trade("HPG", BoardId.ROUND_LOT)
        print("latest_trade:", trades[0].match_price if trades else "no trades")

        # Orders — read-only (no OTP)
        orders = await client.orders.list(ACCOUNT_NO, market_type="STOCK", order_category="NORMAL")
        print("open orders:", len(orders.orders or []))

        # Deals
        deals = await client.deals.list(ACCOUNT_NO, market_type="STOCK")
        print("deals:", len(deals.deals or []))


asyncio.run(main())
