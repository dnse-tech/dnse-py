"""Tests for DnseStreamBase: dispatch, handler registry, control messages, stop."""

from unittest.mock import AsyncMock

import pytest

from dnse.stream._base_stream import RECONNECT_BASE_DELAY, RECONNECT_MAX_DELAY, DnseStreamBase
from dnse.stream.exceptions import DnseStreamAuthError
from dnse.stream.models import StreamTrade


def make_stream() -> DnseStreamBase:
    return DnseStreamBase(api_key="testkey", api_secret="testsecret")


# --- Handler registry ---


def test_ensure_coroutine_rejects_sync():
    def sync_fn(x): ...

    with pytest.raises(TypeError, match="async function"):
        make_stream()._ensure_coroutine(sync_fn)


def test_ensure_coroutine_accepts_async():
    async def async_fn(x): ...

    make_stream()._ensure_coroutine(async_fn)  # should not raise


def test_register_handler_stores_in_registry():
    stream = make_stream()

    async def handler(msg): ...

    stream._register_handler("t", "VIC", handler)
    assert stream._handlers["t"]["VIC"] is handler


def test_register_handler_wildcard():
    stream = make_stream()

    async def handler(msg): ...

    stream._register_handler("o", "*", handler)
    assert stream._handlers["o"]["*"] is handler


# --- Dispatch ---


@pytest.mark.asyncio
async def test_dispatch_calls_exact_symbol_handler():
    stream = make_stream()
    received = []

    async def handler(msg):
        received.append(msg)

    stream._register_handler("t", "VIC", handler)
    await stream._dispatch({"T": "t", "symbol": "VIC", "price": 98.5})
    assert len(received) == 1
    assert isinstance(received[0], StreamTrade)
    assert received[0].price == 98.5


@pytest.mark.asyncio
async def test_dispatch_falls_back_to_wildcard():
    stream = make_stream()
    received = []

    async def handler(msg):
        received.append(msg)

    stream._register_handler("o", "*", handler)
    await stream._dispatch({"T": "o", "orderId": "ORD1"})
    assert len(received) == 1


@pytest.mark.asyncio
async def test_dispatch_no_handler_does_nothing():
    await make_stream()._dispatch({"T": "t", "symbol": "VIC"})


@pytest.mark.asyncio
async def test_dispatch_unknown_t_passes_raw_dict():
    stream = make_stream()
    received = []

    async def handler(msg):
        received.append(msg)

    stream._register_handler("z", "*", handler)
    await stream._dispatch({"T": "z", "data": "raw"})
    assert received[0] == {"T": "z", "data": "raw"}


# --- Control messages ---


@pytest.mark.asyncio
async def test_handle_control_ping_sends_pong():
    stream = make_stream()
    stream._ws = AsyncMock()
    await stream._handle_control({"action": "ping"})
    stream._ws.send.assert_called_once()
    assert "pong" in stream._ws.send.call_args[0][0]


@pytest.mark.asyncio
async def test_handle_control_pong_is_noop():
    stream = make_stream()
    stream._ws = AsyncMock()
    await stream._handle_control({"action": "pong"})
    stream._ws.send.assert_not_called()


@pytest.mark.asyncio
async def test_handle_control_auth_error_raises():
    stream = make_stream()
    stream._ws = AsyncMock()
    with pytest.raises(DnseStreamAuthError):
        await stream._handle_control({"action": "auth_error", "message": "bad key"})


# --- Stop ---


def test_stop_sets_should_run_false():
    stream = make_stream()
    stream._should_run = True
    stream._loop = None
    stream.stop()
    assert stream._should_run is False


# --- Subscribe ---


def test_subscribe_stores_channels():
    stream = make_stream()
    ch = {"name": "tick.G1.json", "symbols": ["VIC"]}
    stream.subscribe([ch])
    assert ch in stream._subscriptions


def test_subscribe_deduplicates():
    stream = make_stream()
    ch = {"name": "orders"}
    stream.subscribe([ch])
    stream.subscribe([ch])
    assert stream._subscriptions.count(ch) == 1


def test_unsubscribe_removes_channel():
    stream = make_stream()
    ch = {"name": "orders"}
    stream.subscribe([ch])
    stream.unsubscribe([ch])
    assert ch not in stream._subscriptions


# --- Reconnect backoff ---


def test_reconnect_delay_stays_within_bounds():
    delays = [min(RECONNECT_BASE_DELAY * (2**i), RECONNECT_MAX_DELAY) for i in range(10)]
    assert delays[0] == 1.0
    assert delays[-1] == RECONNECT_MAX_DELAY
    assert all(d <= RECONNECT_MAX_DELAY for d in delays)
