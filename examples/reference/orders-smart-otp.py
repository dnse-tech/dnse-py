"""Reference: OrdersResource — all methods (SmartOTP mode).

SmartOTP: provide your out-of-band OTP directly (no send_otp call needed).

Run: python reference/orders-smart-otp.py
"""

from dotenv import load_dotenv

load_dotenv()

import os  # noqa: E402

from dnse import DnseClient, PlaceOrderRequest, UpdateOrderRequest  # noqa: E402

ACCOUNT_NO = os.environ["DNSE_ACCOUNT_NO"]

with DnseClient(
    api_key=os.environ["DNSE_API_KEY"], api_secret=os.environ["DNSE_API_SECRET"]
) as client:
    # list() — active orders
    orders = client.orders.list(ACCOUNT_NO, marketType="STOCK")
    print("orders.list():", orders)

    # history() — historical orders
    history = client.orders.history(
        ACCOUNT_NO, **{"from": "2026-01-01", "to": "2026-03-01"}, marketType="STOCK"
    )
    print("\norders.history():", history)

    # --- mutations require trading token ---
    otp = input("\nEnter SmartOTP (or Enter to skip): ").strip()  # noqa: S322
    if not otp:
        print("Skipping place/update/cancel examples.")
    else:
        client.registration.verify_otp(otp, otp_type="smart_otp")

        # place()
        order = client.orders.place(
            PlaceOrderRequest(
                account_no=ACCOUNT_NO,
                symbol="HPG",
                side="NB",
                order_type="LO",
                quantity=100,
                price=10000.0,
            )
        )
        print("\norders.place():", order)

        # get()
        detail = client.orders.get(ACCOUNT_NO, order.id or 0)
        print("\norders.get():", detail)

        # update()
        updated = client.orders.update(
            ACCOUNT_NO,
            order.id or 0,
            UpdateOrderRequest(quantity=200),
        )
        print("\norders.update():", updated)

        # cancel()
        client.orders.cancel(ACCOUNT_NO, order.id or 0)
        print(f"\norders.cancel(): order {order.id} cancelled")
