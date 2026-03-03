"""Pydantic v2 models for DNSE WebSocket stream data types.

T field values: t=Trade, te=TradeExtra, q=Quote, b=OHLC,
e=ExpectedPrice, sd=SecurityDef, o=Order, p=Position, a=AccountUpdate
"""

from __future__ import annotations

from dnse.models.base import DnseBaseModel


class StreamTrade(DnseBaseModel):
    """Trade tick data (T="t")."""

    symbol: str | None = None
    price: float | None = None
    volume: int | None = None
    timestamp: int | None = None
    side: str | None = None


class StreamTradeExtra(DnseBaseModel):
    """Extended trade data with additional fields (T="te")."""

    symbol: str | None = None
    price: float | None = None
    volume: int | None = None
    timestamp: int | None = None
    side: str | None = None
    total_volume: int | None = None
    total_value: float | None = None


class StreamQuote(DnseBaseModel):
    """Best bid/ask quote data (T="q")."""

    symbol: str | None = None
    bid_price: float | None = None
    bid_volume: int | None = None
    ask_price: float | None = None
    ask_volume: int | None = None
    timestamp: int | None = None


class StreamOhlc(DnseBaseModel):
    """OHLC candlestick bar data (T="b")."""

    symbol: str | None = None
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: int | None = None
    timeframe: str | None = None
    timestamp: int | None = None


class StreamExpectedPrice(DnseBaseModel):
    """Expected/reference price data (T="e")."""

    symbol: str | None = None
    price: float | None = None
    volume: int | None = None
    timestamp: int | None = None


class StreamSecurityDef(DnseBaseModel):
    """Security definition with price limits (T="sd")."""

    symbol: str | None = None
    ceiling: float | None = None
    floor: float | None = None
    ref_price: float | None = None


class StreamOrder(DnseBaseModel):
    """Order update event (T="o")."""

    order_id: str | None = None
    symbol: str | None = None
    side: str | None = None
    qty: int | None = None
    price: float | None = None
    status: str | None = None
    timestamp: int | None = None


class StreamPosition(DnseBaseModel):
    """Position update event (T="p")."""

    symbol: str | None = None
    qty: int | None = None
    avg_price: float | None = None
    market_value: float | None = None


class StreamAccountUpdate(DnseBaseModel):
    """Account balance/equity update (T="a")."""

    account_no: str | None = None
    balance: float | None = None
    equity: float | None = None


# Maps T field value → model class for dispatch
TYPE_MAP: dict[str, type[DnseBaseModel]] = {
    "t": StreamTrade,
    "te": StreamTradeExtra,
    "q": StreamQuote,
    "b": StreamOhlc,
    "e": StreamExpectedPrice,
    "sd": StreamSecurityDef,
    "o": StreamOrder,
    "p": StreamPosition,
    "a": StreamAccountUpdate,
}
