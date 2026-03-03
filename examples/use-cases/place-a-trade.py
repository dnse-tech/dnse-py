"""Place a Trade — full flow: OTP → place buy order → cancel it.

⚠️  THIS PLACES A REAL ORDER on your account.
    A limit order priced well below market ensures it won't fill before cancel.

Setup: cp .env.example .env → fill ALL vars → pip install "dnse[examples]"
Run:   python use-cases/place-a-trade.py
"""

from dotenv import load_dotenv

load_dotenv()

import os  # noqa: E402

from dnse import DnseClient, PlaceOrderRequest  # noqa: E402

ACCOUNT_NO = os.environ["DNSE_ACCOUNT_NO"]
SYMBOL = "HPG"
QUANTITY = 100  # minimum board lot
PRICE = 10000.0  # deliberately low limit → won't fill

with DnseClient(
    api_key=os.environ["DNSE_API_KEY"], api_secret=os.environ["DNSE_API_SECRET"]
) as client:
    # Step 1: OTP
    client.registration.send_otp()
    otp = input("Enter OTP from email: ").strip()  # noqa: S322
    client.registration.verify_otp(otp)

    # Step 2: Safety prompt
    print("\n⚠️  About to place a REAL BUY order:")
    print(f"   Symbol={SYMBOL}  Qty={QUANTITY}  Price={PRICE}  Account={ACCOUNT_NO}")
    input("Press Enter to continue or Ctrl+C to abort: ")  # noqa: S322

    # Step 3: Place order
    order = client.orders.place(
        PlaceOrderRequest(
            account_no=ACCOUNT_NO,
            symbol=SYMBOL,
            side="NB",  # NB = buy
            order_type="LO",  # limit order
            quantity=QUANTITY,
            price=PRICE,
        )
    )
    print(f"\nOrder placed: id={order.id}  status={order.status}")

    # Step 4: Cancel order
    client.orders.cancel(ACCOUNT_NO, order.id or 0)
    print(f"Order {order.id} cancelled.")
