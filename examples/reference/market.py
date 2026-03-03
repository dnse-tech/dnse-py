"""Reference: MarketResource — all methods.

No OTP required.

Run: python reference/market.py
"""

from dotenv import load_dotenv

load_dotenv()

import os  # noqa: E402

from dnse import DnseClient  # noqa: E402

with DnseClient(
    api_key=os.environ["DNSE_API_KEY"], api_secret=os.environ["DNSE_API_SECRET"]
) as client:
    # Returns list — one SecurityDefinition per board
    secs = client.market.security_info("HPG")
    print(f"market.security_info('HPG'): {len(secs)} board(s)")
    for sec in secs:
        board = sec.board_id
        ceiling = sec.ceiling_price
        floor = sec.floor_price
        basic = sec.basic_price
        print(f"  board={board}  ceiling={ceiling}  floor={floor}  basic={basic}")

    # Filter to a specific board using BoardId enum
    from dnse import BoardId  # noqa: E402

    round_lot = client.market.security_info("HPG", board_id=BoardId.ROUND_LOT)
    if round_lot:
        print(f"\nRound lot board: {round_lot[0]}")
