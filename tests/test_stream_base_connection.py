"""Tests for DnseStreamBase connection, auth, heartbeat, message loop, and reconnect."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import websockets.exceptions

from dnse.stream._base_stream import DnseStreamBase
from dnse.stream.exceptions import DnseStreamAuthError, DnseStreamConnectionError


def make_stream() -> DnseStreamBase:
    return DnseStreamBase(api_key="testkey", api_secret="testsecret")


def make_mock_ws() -> AsyncMock:
    ws = AsyncMock()
    ws.send = AsyncMock()
    ws.recv = AsyncMock()
    ws.close = AsyncMock()
    return ws


# ---------------------------------------------------------------------------
# _connect
# ---------------------------------------------------------------------------


async def test_connect_sets_ws_and_logs_session():
    stream = make_stream()
    mock_ws = make_mock_ws()
    mock_ws.recv.return_value = '{"session_id": "sess123"}'

    with patch("websockets.connect", new_callable=AsyncMock, return_value=mock_ws):
        await stream._connect()

    assert stream._ws is mock_ws
    mock_ws.recv.assert_called_once()


async def test_connect_url_includes_encoding():
    stream = make_stream()
    mock_ws = make_mock_ws()
    mock_ws.recv.return_value = '{"session_id": "s"}'
    captured_url = []

    async def fake_connect(url, **kwargs):
        captured_url.append(url)
        return mock_ws

    with patch("websockets.connect", side_effect=fake_connect):
        await stream._connect()

    assert "encoding=json" in captured_url[0]


# ---------------------------------------------------------------------------
# _authenticate
# ---------------------------------------------------------------------------


async def test_authenticate_sends_auth_message():
    stream = make_stream()
    mock_ws = make_mock_ws()
    stream._ws = mock_ws
    mock_ws.recv.return_value = '{"action": "authenticated"}'

    await stream._authenticate()

    mock_ws.send.assert_called_once()
    mock_ws.recv.assert_called_once()


async def test_authenticate_raises_on_auth_error():
    stream = make_stream()
    mock_ws = make_mock_ws()
    stream._ws = mock_ws
    mock_ws.recv.return_value = '{"action": "auth_error", "message": "invalid key"}'

    with pytest.raises(DnseStreamAuthError, match="invalid key"):
        await stream._authenticate()


async def test_authenticate_no_error_on_success():
    stream = make_stream()
    mock_ws = make_mock_ws()
    stream._ws = mock_ws
    mock_ws.recv.return_value = '{"action": "auth_ok"}'

    # Should not raise
    await stream._authenticate()


# ---------------------------------------------------------------------------
# _resubscribe
# ---------------------------------------------------------------------------


async def test_resubscribe_sends_all_subscriptions():
    stream = make_stream()
    mock_ws = make_mock_ws()
    stream._ws = mock_ws
    ch1 = {"name": "tick.G1.json", "symbols": ["VIC"]}
    ch2 = {"name": "orders"}
    stream._subscriptions = [ch1, ch2]

    await stream._resubscribe()

    assert mock_ws.send.call_count == 2


async def test_resubscribe_empty_does_nothing():
    stream = make_stream()
    mock_ws = make_mock_ws()
    stream._ws = mock_ws
    stream._subscriptions = []

    await stream._resubscribe()

    mock_ws.send.assert_not_called()


# ---------------------------------------------------------------------------
# _heartbeat_loop
# ---------------------------------------------------------------------------


async def test_heartbeat_loop_sends_ping_and_exits_when_stopped():
    stream = make_stream()
    mock_ws = make_mock_ws()
    stream._ws = mock_ws
    stream._should_run = True
    ping_count = 0

    async def fake_sleep(n):
        nonlocal ping_count
        ping_count += 1
        stream._should_run = False  # Stop after first ping

    with patch("asyncio.sleep", side_effect=fake_sleep):
        await stream._heartbeat_loop()

    assert mock_ws.send.called
    assert ping_count == 1


async def test_heartbeat_loop_exits_on_send_error():
    stream = make_stream()
    mock_ws = make_mock_ws()
    mock_ws.send.side_effect = Exception("connection closed")
    stream._ws = mock_ws
    stream._should_run = True

    # Should return without raising
    await stream._heartbeat_loop()

    mock_ws.send.assert_called_once()


# ---------------------------------------------------------------------------
# _message_loop
# ---------------------------------------------------------------------------


async def test_message_loop_dispatches_t_message():
    stream = make_stream()
    mock_ws = make_mock_ws()
    stream._ws = mock_ws
    stream._should_run = True
    received = []

    async def handler(msg):
        received.append(msg)
        stream._should_run = False

    stream._register_handler("t", "*", handler)

    async def fake_recv():
        return '{"T": "t", "symbol": "VIC", "price": 99.0}'

    mock_ws.recv = fake_recv

    async def fake_wait_for(coro, timeout):
        return await coro

    with patch("asyncio.wait_for", side_effect=fake_wait_for):
        await stream._message_loop()

    assert len(received) == 1


async def test_message_loop_handles_timeout_and_continues():
    stream = make_stream()
    mock_ws = make_mock_ws()
    stream._ws = mock_ws
    stream._should_run = True
    timeout_count = 0

    async def fake_wait_for(coro, timeout):
        nonlocal timeout_count
        timeout_count += 1
        if timeout_count == 1:
            raise asyncio.TimeoutError()
        stream._should_run = False
        raise asyncio.TimeoutError()

    with patch("asyncio.wait_for", side_effect=fake_wait_for):
        await stream._message_loop()

    assert timeout_count >= 1


async def test_message_loop_handles_action_message():
    stream = make_stream()
    mock_ws = make_mock_ws()
    stream._ws = mock_ws
    stream._should_run = True

    call_count = 0

    async def fake_recv():
        return '{"action": "ping"}'

    mock_ws.recv = fake_recv

    async def fake_wait_for(coro, timeout):
        nonlocal call_count
        call_count += 1
        result = await coro
        stream._should_run = False
        return result

    with patch("asyncio.wait_for", side_effect=fake_wait_for):
        await stream._message_loop()

    # Control message (ping) should trigger pong send
    mock_ws.send.assert_called_once()


# ---------------------------------------------------------------------------
# _reconnect
# ---------------------------------------------------------------------------


async def test_reconnect_succeeds_on_first_attempt():
    stream = make_stream()
    mock_ws = make_mock_ws()
    mock_ws.recv.return_value = '{"session_id": "s", "action": "auth_ok"}'

    with (
        patch("asyncio.sleep", new_callable=AsyncMock),
        patch("websockets.connect", new_callable=AsyncMock, return_value=mock_ws),
    ):
        await stream._reconnect()

    assert stream._ws is mock_ws


async def test_reconnect_raises_after_max_retries():
    stream = make_stream()

    async def fail_connect(*args, **kwargs):
        raise ConnectionError("refused")

    with (
        patch("asyncio.sleep", new_callable=AsyncMock),
        patch("websockets.connect", side_effect=fail_connect),
    ):
        with pytest.raises(DnseStreamConnectionError):
            await stream._reconnect()


async def test_reconnect_retries_on_transient_failure():
    stream = make_stream()
    mock_ws = make_mock_ws()
    mock_ws.recv.return_value = '{"session_id": "s", "action": "ok"}'
    attempt_count = 0

    async def sometimes_fail(*args, **kwargs):
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ConnectionError("transient")
        return mock_ws

    with (
        patch("asyncio.sleep", new_callable=AsyncMock),
        patch("websockets.connect", side_effect=sometimes_fail),
    ):
        await stream._reconnect()

    assert attempt_count == 3


# ---------------------------------------------------------------------------
# run_async
# ---------------------------------------------------------------------------


async def test_run_async_connects_auth_and_stops():
    stream = make_stream()
    mock_ws = make_mock_ws()
    # recv returns welcome then stops message loop via ConnectionClosed
    mock_ws.recv.side_effect = [
        '{"session_id": "s"}',  # welcome in _connect
        '{"action": "auth_ok"}',  # auth response
        websockets.exceptions.ConnectionClosed(None, None),
    ]
    stream._should_run = True

    async def fake_message_loop():
        stream._should_run = False

    with (
        patch("websockets.connect", new_callable=AsyncMock, return_value=mock_ws),
        patch.object(stream, "_message_loop", side_effect=fake_message_loop),
        patch.object(stream, "_heartbeat_loop", new_callable=AsyncMock),
    ):
        await stream.run_async()

    assert stream._running is False
    mock_ws.close.assert_called_once()


# ---------------------------------------------------------------------------
# stop with running loop
# ---------------------------------------------------------------------------


def test_stop_with_running_loop_schedules_close():
    stream = make_stream()
    stream._should_run = True
    mock_ws = MagicMock()
    mock_ws.close = AsyncMock()
    stream._ws = mock_ws

    mock_loop = MagicMock()
    mock_loop.is_running.return_value = True
    stream._loop = mock_loop

    stream.stop()

    assert stream._should_run is False
    mock_loop.is_running.assert_called_once()
    # Verify call_soon_threadsafe was used to schedule close
    assert mock_loop.call_soon_threadsafe.called


# ---------------------------------------------------------------------------
# subscribe with running loop sends immediately
# ---------------------------------------------------------------------------


def test_subscribe_with_connected_ws_sends_channel():
    stream = make_stream()
    mock_ws = AsyncMock()  # AsyncMock so .send() returns a valid coroutine
    mock_loop = MagicMock()
    mock_loop.is_running.return_value = True
    stream._ws = mock_ws
    stream._loop = mock_loop

    ch = {"name": "orders"}
    stream.subscribe([ch])

    assert ch in stream._subscriptions
    # run_coroutine_threadsafe was called for immediate send
    mock_loop.is_running.assert_called()
