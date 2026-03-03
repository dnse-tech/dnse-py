"""DnseTradingStream — private order/position/account subscriptions over WebSocket."""

from __future__ import annotations

from dnse.stream._base_stream import AsyncHandler, DnseStreamBase


class DnseTradingStream(DnseStreamBase):
    """WebSocket stream for private trading events: orders, positions, account.

    All subscribe_* methods are sync — register handler before calling run().

    Example:
        stream = DnseTradingStream(api_key="...", api_secret="...")

        async def on_order(order):
            print(order.order_id, order.status)

        stream.subscribe_orders(on_order)
        stream.run()
    """

    def subscribe_orders(self, handler: AsyncHandler) -> None:
        """Subscribe to order update events (T="o").

        Args:
            handler: Async callable receiving StreamOrder instances.
        """
        self._register_handler("o", "*", handler)
        self.subscribe([{"name": "orders"}])

    def subscribe_positions(self, handler: AsyncHandler) -> None:
        """Subscribe to position update events (T="p").

        Args:
            handler: Async callable receiving StreamPosition instances.
        """
        self._register_handler("p", "*", handler)
        self.subscribe([{"name": "positions"}])

    def subscribe_account(self, handler: AsyncHandler) -> None:
        """Subscribe to account balance/equity update events (T="a").

        Args:
            handler: Async callable receiving StreamAccountUpdate instances.
        """
        self._register_handler("a", "*", handler)
        self.subscribe([{"name": "account"}])
