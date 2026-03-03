"""Reference: DnseTradingStream — subscribe to private trading events over WebSocket.

Streams for ~30 seconds then exits.

Run: python reference/trading-stream.py
"""

from dotenv import load_dotenv

load_dotenv()

import asyncio  # noqa: E402
import os  # noqa: E402

from dnse import DnseTradingStream  # noqa: E402

stream = DnseTradingStream(
    api_key=os.environ["DNSE_API_KEY"],
    api_secret=os.environ["DNSE_API_SECRET"],
)


async def on_order(msg):  # noqa: D103
    print(f"[order]    {msg}")


async def on_position(msg):  # noqa: D103
    print(f"[position] {msg}")


async def on_account(msg):  # noqa: D103
    print(f"[account]  {msg}")


stream.subscribe_orders(on_order)
stream.subscribe_positions(on_position)
stream.subscribe_account(on_account)


async def main():
    """Run stream for 30 seconds."""
    task = asyncio.create_task(asyncio.to_thread(stream.run))
    await asyncio.sleep(30)
    task.cancel()


asyncio.run(main())
