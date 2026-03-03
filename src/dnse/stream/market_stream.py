"""DnseMarketStream — public market data subscriptions over WebSocket."""

from __future__ import annotations

from dnse.stream._base_stream import AsyncHandler, DnseStreamBase


def _normalize_symbols(symbols: str | list[str]) -> list[str]:
    """Return symbols as a list regardless of input type."""
    return [symbols] if isinstance(symbols, str) else list(symbols)


class DnseMarketStream(DnseStreamBase):
    """WebSocket stream for public market data: trades, quotes, OHLC, etc.

    All subscribe_* methods are sync — register handler before calling run().

    Example:
        stream = DnseMarketStream(api_key="...", api_secret="...")

        async def on_trade(trade):
            print(trade.price, trade.volume)

        stream.subscribe_trades(["VIC", "VNM"], on_trade)
        stream.run()
    """

    def subscribe_trades(self, symbols: str | list[str], handler: AsyncHandler) -> None:
        """Subscribe to trade tick data (T="t") for given symbols.

        Args:
            symbols: Ticker symbol or list of symbols.
            handler: Async callable receiving StreamTrade instances.
        """
        sym_list = _normalize_symbols(symbols)
        for sym in sym_list:
            self._register_handler("t", sym, handler)
        self.subscribe([{"name": "tick.G1.json", "symbols": sym_list}])

    def subscribe_quotes(self, symbols: str | list[str], handler: AsyncHandler) -> None:
        """Subscribe to best bid/ask quote data (T="q") for given symbols.

        Args:
            symbols: Ticker symbol or list of symbols.
            handler: Async callable receiving StreamQuote instances.
        """
        sym_list = _normalize_symbols(symbols)
        for sym in sym_list:
            self._register_handler("q", sym, handler)
        self.subscribe([{"name": "tick.G1.json", "symbols": sym_list}])

    def subscribe_ohlc(
        self,
        symbols: str | list[str],
        handler: AsyncHandler,
        *,
        timeframe: str = "1m",
    ) -> None:
        """Subscribe to OHLC candlestick bars (T="b") for given symbols.

        Args:
            symbols: Ticker symbol or list of symbols.
            handler: Async callable receiving StreamOhlc instances.
            timeframe: Bar interval, e.g. "1m", "5m", "1h". Defaults to "1m".
        """
        sym_list = _normalize_symbols(symbols)
        for sym in sym_list:
            self._register_handler("b", sym, handler)
        self.subscribe([{"name": f"ohlc.{timeframe}.json", "symbols": sym_list}])

    def subscribe_expected_price(self, symbols: str | list[str], handler: AsyncHandler) -> None:
        """Subscribe to expected/reference price data (T="e") for given symbols.

        Args:
            symbols: Ticker symbol or list of symbols.
            handler: Async callable receiving StreamExpectedPrice instances.
        """
        sym_list = _normalize_symbols(symbols)
        for sym in sym_list:
            self._register_handler("e", sym, handler)
        self.subscribe([{"name": "tick.G1.json", "symbols": sym_list}])

    def subscribe_security_def(self, symbols: str | list[str], handler: AsyncHandler) -> None:
        """Subscribe to security definition data (T="sd") for given symbols.

        Args:
            symbols: Ticker symbol or list of symbols.
            handler: Async callable receiving StreamSecurityDef instances.
        """
        sym_list = _normalize_symbols(symbols)
        for sym in sym_list:
            self._register_handler("sd", sym, handler)
        self.subscribe([{"name": "tick.G1.json", "symbols": sym_list}])
