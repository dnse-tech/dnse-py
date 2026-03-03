"""Reference: DnseMarketStream — subscribe to market data over WebSocket.

Streams for ~10 seconds then exits.

Run: python reference/market-stream.py
"""

from dotenv import load_dotenv

load_dotenv()

import asyncio  # noqa: E402
import os  # noqa: E402

from dnse import DnseMarketStream  # noqa: E402

stream = DnseMarketStream(
    api_key=os.environ["DNSE_API_KEY"],
    api_secret=os.environ["DNSE_API_SECRET"],
)


async def on_trade(msg):  # noqa: D103
    print(f"[trade] {msg}")


async def on_quote(msg):  # noqa: D103
    print(f"[quote] {msg}")


async def on_ohlc(msg):  # noqa: D103
    print(f"[ohlc]  {msg}")


async def on_expected_price(msg):  # noqa: D103
    print(f"[exp]   {msg}")


async def on_secdef(msg):  # noqa: D103
    print(f"[secdef]{msg}")


stream.subscribe_trades(["HPG", "VIC"], on_trade)
stream.subscribe_quotes(["HPG"], on_quote)
stream.subscribe_ohlc(["HPG"], on_ohlc, timeframe="1m")
stream.subscribe_expected_price(["HPG"], on_expected_price)
stream.subscribe_security_def(["HPG"], on_secdef)


async def main():
    """Run stream for 10 seconds."""
    task = asyncio.create_task(asyncio.to_thread(stream.run))
    await asyncio.sleep(10)
    task.cancel()


asyncio.run(main())
