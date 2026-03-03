"""Order History — fetch historical orders and today's deals.

No OTP required.

Setup: cp .env.example .env → fill ALL vars → pip install "dnse[examples]"
Run:   python use-cases/order-history.py
"""

from dotenv import load_dotenv

load_dotenv()

import os  # noqa: E402
from datetime import date, timedelta  # noqa: E402

from dnse import DnseClient  # noqa: E402

ACCOUNT_NO = os.environ["DNSE_ACCOUNT_NO"]

with DnseClient(
    api_key=os.environ["DNSE_API_KEY"], api_secret=os.environ["DNSE_API_SECRET"]
) as client:
    # Last 30 days of order history
    to_date = date.today().isoformat()
    from_date = (date.today() - timedelta(days=30)).isoformat()

    history = client.orders.history(
        ACCOUNT_NO,
        **{"from": from_date, "to": to_date},
        marketType="STOCK",
    )
    print(f"Order history ({from_date} → {to_date}): {len(history.orders or [])} orders")
    for o in (history.orders or [])[:5]:
        print(f"  {o.order_id}  {o.symbol}  {o.side}  qty={o.quantity}  status={o.status}")

    # Today's deals
    deals = client.deals.list(ACCOUNT_NO)
    print(f"\nDeals today: {len(deals.deals or [])}")
    for d in (deals.deals or [])[:5]:
        print(f"  {d.symbol}  qty={d.quantity}  price={d.price}")
