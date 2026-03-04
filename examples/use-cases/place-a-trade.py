"""Place a Trade — full flow: OTP → place buy order → cancel it.

⚠️  THIS PLACES A REAL ORDER on your account.
    Uses the floor price from security info to ensure a valid price range.

Setup: cp .env.example .env → fill ALL vars → pip install "dnse[examples]"
Run:   python use-cases/place-a-trade.py
"""

from dotenv import load_dotenv

load_dotenv()

import os  # noqa: E402

from dnse import BoardId, DnseClient, PlaceOrderRequest  # noqa: E402

ACCOUNT_NO = os.environ["DNSE_ACCOUNT_NO"]
SYMBOL = "HPG"
QUANTITY = 100  # minimum board lot

with DnseClient(
    api_key=os.environ["DNSE_API_KEY"], api_secret=os.environ["DNSE_API_SECRET"]
) as client:
    # Step 1: Fetch security info to get valid price range
    secs = client.market.security_info(SYMBOL, board_id=BoardId.ROUND_LOT)
    sec = secs[0]
    PRICE = sec.floor_price  # use floor price to stay within valid range
    print(
        f"Security: ceiling={sec.ceiling_price}  floor={sec.floor_price}  basic={sec.basic_price}"
    )
    print(f"Using floor price: {PRICE}")

    # Step 2: OTP
    client.registration.send_otp()
    otp = input("Enter OTP from email: ").strip()  # noqa: S322
    client.registration.verify_otp(otp)

    # Step 3: Safety prompt
    print("\n⚠️  About to place a REAL BUY order:")
    print(f"   Symbol={SYMBOL}  Qty={QUANTITY}  Price={PRICE}  Account={ACCOUNT_NO}")
    input("Press Enter to continue or Ctrl+C to abort: ")  # noqa: S322

    # Step 4: Place order
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

    # Step 5: Cancel order
    client.orders.cancel(ACCOUNT_NO, order.id or 0)
    print(f"Order {order.id} cancelled.")
