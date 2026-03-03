"""Tests for DnseMarketStream and DnseTradingStream subscription methods."""

from dnse.stream.market_stream import DnseMarketStream, _normalize_symbols
from dnse.stream.trading_stream import DnseTradingStream


async def dummy_handler(msg): ...


def make_market() -> DnseMarketStream:
    return DnseMarketStream(api_key="k", api_secret="s")


def make_trading() -> DnseTradingStream:
    return DnseTradingStream(api_key="k", api_secret="s")


# --- _normalize_symbols ---


def test_normalize_symbols_string():
    assert _normalize_symbols("VIC") == ["VIC"]


def test_normalize_symbols_list():
    assert _normalize_symbols(["VIC", "VNM"]) == ["VIC", "VNM"]


# --- DnseMarketStream ---


def test_subscribe_trades_registers_handler():
    s = make_market()
    s.subscribe_trades("VIC", dummy_handler)
    assert s._handlers["t"]["VIC"] is dummy_handler


def test_subscribe_trades_list_registers_all():
    s = make_market()
    s.subscribe_trades(["VIC", "VNM"], dummy_handler)
    assert "VIC" in s._handlers["t"] and "VNM" in s._handlers["t"]


def test_subscribe_trades_adds_subscription():
    s = make_market()
    s.subscribe_trades(["VIC"], dummy_handler)
    assert any(sub["name"] == "tick.G1.json" for sub in s._subscriptions)


def test_subscribe_quotes_registers_q_handler():
    s = make_market()
    s.subscribe_quotes("FPT", dummy_handler)
    assert s._handlers["q"]["FPT"] is dummy_handler


def test_subscribe_ohlc_default_timeframe():
    s = make_market()
    s.subscribe_ohlc("VIC", dummy_handler)
    assert any(sub["name"] == "ohlc.1m.json" for sub in s._subscriptions)


def test_subscribe_ohlc_custom_timeframe():
    s = make_market()
    s.subscribe_ohlc("VIC", dummy_handler, timeframe="5m")
    assert any(sub["name"] == "ohlc.5m.json" for sub in s._subscriptions)


def test_subscribe_ohlc_registers_b_handler():
    s = make_market()
    s.subscribe_ohlc("VIC", dummy_handler)
    assert s._handlers["b"]["VIC"] is dummy_handler


def test_subscribe_expected_price_registers_e_handler():
    s = make_market()
    s.subscribe_expected_price("HPG", dummy_handler)
    assert s._handlers["e"]["HPG"] is dummy_handler


def test_subscribe_security_def_registers_sd_handler():
    s = make_market()
    s.subscribe_security_def("MSN", dummy_handler)
    assert s._handlers["sd"]["MSN"] is dummy_handler


# --- DnseTradingStream ---


def test_subscribe_orders_wildcard_and_channel():
    s = make_trading()
    s.subscribe_orders(dummy_handler)
    assert s._handlers["o"]["*"] is dummy_handler
    assert any(sub["name"] == "orders" for sub in s._subscriptions)


def test_subscribe_positions_wildcard_and_channel():
    s = make_trading()
    s.subscribe_positions(dummy_handler)
    assert s._handlers["p"]["*"] is dummy_handler
    assert any(sub["name"] == "positions" for sub in s._subscriptions)


def test_subscribe_account_wildcard_and_channel():
    s = make_trading()
    s.subscribe_account(dummy_handler)
    assert s._handlers["a"]["*"] is dummy_handler
    assert any(sub["name"] == "account" for sub in s._subscriptions)
