"""Base WebSocket stream: connection, auth, heartbeat, reconnect, dispatch."""

from __future__ import annotations

import asyncio
import inspect
import logging
import threading
from collections.abc import Callable, Coroutine
from typing import Any

import websockets
import websockets.exceptions

from dnse.stream._stream_auth import build_auth_message
from dnse.stream._stream_encoding import StreamEncoder
from dnse.stream.exceptions import DnseStreamAuthError, DnseStreamConnectionError
from dnse.stream.models import TYPE_MAP

WS_BASE_URL = "wss://ws-openapi.dnse.com.vn/v1/stream"
MAX_RECONNECT_RETRIES = 10
RECONNECT_BASE_DELAY = 1.0
RECONNECT_MAX_DELAY = 60.0
RECV_TIMEOUT = 5.0

_log = logging.getLogger("dnse.stream")
AsyncHandler = Callable[..., Coroutine[Any, Any, None]]


class DnseStreamBase:
    """Base class handling WS lifecycle: connect, auth, heartbeat, reconnect, dispatch."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        encoding: str = "json",
        heartbeat_interval: int = 30,
    ) -> None:
        """Initialize stream with credentials and optional encoding.

        Args:
            api_key: DNSE API key.
            api_secret: DNSE API secret.
            encoding: Wire encoding — "json" (default) or "msgpack".
            heartbeat_interval: Seconds between ping messages.
        """
        self._api_key = api_key
        self._api_secret = api_secret
        self._encoder = StreamEncoder(encoding)
        self._heartbeat_interval = heartbeat_interval
        self._should_run = False
        self._running = False
        self._ws: Any = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._handlers: dict[str, dict[str, AsyncHandler]] = {}
        self._subscriptions: list[dict[str, Any]] = []

    async def _connect(self) -> None:
        url = f"{WS_BASE_URL}?encoding={self._encoder.query_param}"
        self._ws = await websockets.connect(url, ssl=True)  # type: ignore[attr-defined]
        welcome = self._encoder.decode(await self._ws.recv())
        _log.debug("Connected, session: %s", welcome.get("session_id"))

    async def _authenticate(self) -> None:
        msg = build_auth_message(self._api_key, self._api_secret)
        await self._ws.send(self._encoder.encode(msg))
        resp = self._encoder.decode(await self._ws.recv())
        if resp.get("action") == "auth_error":
            raise DnseStreamAuthError(str(resp.get("message", "Auth failed")))

    async def _resubscribe(self) -> None:
        for sub in self._subscriptions:
            await self._ws.send(self._encoder.encode(sub))

    async def _heartbeat_loop(self) -> None:
        while self._should_run:
            try:
                await self._ws.send(self._encoder.encode({"action": "ping"}))
            except Exception:
                return  # Connection gone; reconnect loop handles it
            await asyncio.sleep(self._heartbeat_interval)

    async def _dispatch(self, msg: dict[str, Any]) -> None:
        t_val = str(msg.get("T") or msg.get("t") or "")
        if not t_val:
            return
        symbol = str(msg.get("symbol") or msg.get("s") or "*")
        t_handlers = self._handlers.get(t_val, {})
        handler = t_handlers.get(symbol) or t_handlers.get("*")
        if handler is None:
            return
        model_cls = TYPE_MAP.get(t_val)
        await handler(model_cls.model_validate(msg) if model_cls else msg)

    async def _handle_control(self, msg: dict[str, Any]) -> None:
        action = msg.get("action")
        if action == "ping":
            await self._ws.send(self._encoder.encode({"action": "pong"}))
        elif action == "auth_error":
            raise DnseStreamAuthError(str(msg.get("message", "Auth error from server")))

    async def _message_loop(self) -> None:
        while self._should_run:
            try:
                data = await asyncio.wait_for(self._ws.recv(), RECV_TIMEOUT)
            except asyncio.TimeoutError:
                continue
            decoded = self._encoder.decode(data)
            if "action" in decoded:
                await self._handle_control(decoded)
            elif "T" in decoded or "t" in decoded:
                await self._dispatch(decoded)

    async def _reconnect(self) -> None:
        for attempt in range(MAX_RECONNECT_RETRIES):
            delay = min(RECONNECT_BASE_DELAY * (2**attempt), RECONNECT_MAX_DELAY)
            await asyncio.sleep(delay)
            try:
                await self._connect()
                await self._authenticate()
                await self._resubscribe()
                return
            except Exception as exc:
                _log.warning("Reconnect attempt %d failed: %s", attempt + 1, exc)
        raise DnseStreamConnectionError("Max reconnect retries exceeded", MAX_RECONNECT_RETRIES)

    async def run_async(self) -> None:
        """Main coroutine: connect, authenticate, run message and heartbeat loops."""
        self._should_run = True
        self._running = True
        self._loop = asyncio.get_running_loop()
        try:
            await self._connect()
            await self._authenticate()
            await self._resubscribe()
            hb_task = asyncio.create_task(self._heartbeat_loop())
            try:
                while self._should_run:
                    try:
                        await self._message_loop()
                    except websockets.exceptions.ConnectionClosed:
                        if self._should_run:
                            _log.info("Connection closed, reconnecting...")
                            await self._reconnect()
            finally:
                hb_task.cancel()
        finally:
            if self._ws:
                await self._ws.close()
            self._running = False

    def run(self) -> None:
        """Block the current thread until the stream stops."""
        asyncio.run(self.run_async())

    def run_in_background(self) -> threading.Thread:
        """Start stream in a daemon thread and return the thread."""
        t = threading.Thread(target=self.run, daemon=True)
        t.start()
        return t

    def stop(self) -> None:
        """Signal the stream to stop gracefully (thread-safe)."""
        self._should_run = False
        if self._loop and self._loop.is_running() and self._ws:
            asyncio.run_coroutine_threadsafe(self._ws.close(), self._loop)

    def subscribe(self, channels: list[dict[str, Any]]) -> None:
        """Register channel subscriptions; sent immediately if connected, else on connect.

        Args:
            channels: List of subscription dicts to send to the server.
        """
        new = [c for c in channels if c not in self._subscriptions]
        self._subscriptions.extend(new)
        if self._ws and self._loop and self._loop.is_running():
            for ch in new:
                asyncio.run_coroutine_threadsafe(
                    self._ws.send(self._encoder.encode(ch)), self._loop
                )

    def unsubscribe(self, channels: list[dict[str, Any]]) -> None:
        """Remove subscriptions from the internal list.

        Args:
            channels: Subscriptions to remove.
        """
        for ch in channels:
            if ch in self._subscriptions:
                self._subscriptions.remove(ch)

    def _ensure_coroutine(self, fn: Any) -> None:
        """Raise TypeError if fn is not an async function."""
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(f"Handler must be an async function, got {type(fn).__name__}")

    def _register_handler(self, t_value: str, symbol: str, handler: AsyncHandler) -> None:
        """Store handler in registry keyed by T field value and symbol.

        Args:
            t_value: T field value (e.g. "t", "q", "o").
            symbol: Ticker symbol or "*" for wildcard.
            handler: Async callable to invoke on matching messages.
        """
        self._ensure_coroutine(handler)
        self._handlers.setdefault(t_value, {})[symbol] = handler
