"""Reference: OrdersResource — all methods (Email OTP mode).

Email OTP: calls send_otp() to trigger an OTP to your registered email,
then prompts you to enter it.

Run: python reference/orders-email-otp.py
"""

import logging

logging.basicConfig(level=logging.DEBUG, format="%(name)s %(levelname)s %(message)s")

from dotenv import load_dotenv

load_dotenv()

import os  # noqa: E402

from dnse import BoardId, DnseClient, PlaceOrderRequest, UpdateOrderRequest  # noqa: E402

ACCOUNT_NO = os.environ["DNSE_ACCOUNT_NO"]

with DnseClient(
    api_key=os.environ["DNSE_API_KEY"], api_secret=os.environ["DNSE_API_SECRET"]
) as client:
    # list() — active orders
    orders = client.orders.list(ACCOUNT_NO, market_type="STOCK", order_category="NORMAL")
    print("orders.list():", orders)

    # history() — historical orders
    history = client.orders.history(
        ACCOUNT_NO, **{"from": "2026-01-01", "to": "2026-03-01"}, marketType="STOCK"
    )
    print("\norders.history():", history)

    # fetch security info to get valid price range
    secs = client.market.security_info("HPG", board_id=BoardId.ROUND_LOT)
    sec = secs[0]
    floor_price = sec.floor_price
    print(
        f"\nmarket.security_info('HPG'): "
        f"ceiling={sec.ceiling_price}  floor={floor_price}  basic={sec.basic_price}"
    )

    # --- mutations require trading token ---
    client.registration.send_otp()
    otp = input("\nEnter OTP from email (or Enter to skip): ").strip()  # noqa: S322
    if not otp:
        print("Skipping place/update/cancel examples.")
    else:
        client.registration.verify_otp(otp)

        # fetch loan packages to get a real loanPackageId (required for place)
        packages = client.accounts.loan_packages(ACCOUNT_NO, market_type="STOCK", symbol="HPG")
        loan_package_id = packages.loan_packages[0].id
        print("\naccounts.loan_packages():", packages)

        # place()
        order = client.orders.place(
            PlaceOrderRequest(
                account_no=ACCOUNT_NO,
                symbol="HPG",
                side="NB",
                order_type="LO",
                quantity=100,
                price=floor_price,  # use floor price to stay within valid range
                loan_package_id=loan_package_id,
            ),
            market_type="STOCK",
            order_category="NORMAL",
        )
        print("\norders.place():", order)

        # get()
        detail = client.orders.get(
            ACCOUNT_NO, order.id or 0, market_type="STOCK", order_category="NORMAL"
        )
        print("\norders.get():", detail)

        # update()
        updated = client.orders.update(
            ACCOUNT_NO,
            order.id or 0,
            UpdateOrderRequest(quantity=200, price=floor_price + 100),
            market_type="STOCK",
            order_category="NORMAL",
        )
        print("\norders.update():", updated)

        # cancel() — update() cancel+replaces, so use the new id from `updated`
        cancel_id = updated.id or 0
        client.orders.cancel(ACCOUNT_NO, cancel_id, market_type="STOCK", order_category="NORMAL")
        print(f"\norders.cancel(): order {cancel_id} cancelled")
