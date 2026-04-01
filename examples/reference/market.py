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

    # Latest trade for a symbol
    trades = client.market.latest_trade("HPG", BoardId.ROUND_LOT)
    print(f"\nmarket.latest_trade('HPG'): {len(trades)} trade(s)")
    for t in trades:
        print(f"  price={t.match_price}  qty={t.match_qtty}  side={t.side}  time={t.time}")

    # Trade history with time range
    history = client.market.trades(
        "HPG", BoardId.ROUND_LOT, from_ts="1711929600", to_ts="1712016000", limit=5
    )
    print(f"\nmarket.trades('HPG', limit=5): {len(history)} trade(s)")
    for t in history:
        print(f"  price={t.match_price}  vol={t.total_volume_traded}  time={t.time}")
