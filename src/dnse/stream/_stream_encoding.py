"""JSON and msgpack encoding/decoding for DNSE WebSocket streams."""

from __future__ import annotations

import json
from typing import Any

from dnse.stream.exceptions import DnseStreamProtocolError


class StreamEncoder:
    """Encode/decode WebSocket messages as JSON or msgpack.

    Args:
        encoding: "json" (default) or "msgpack". msgpack requires
                  the optional ``msgpack`` package to be installed.

    Raises:
        ValueError: If encoding is not "json" or "msgpack".
    """

    _SUPPORTED = ("json", "msgpack")

    def __init__(self, encoding: str = "json") -> None:
        """Initialize encoder.

        Args:
            encoding: Wire encoding — "json" or "msgpack".
        """
        if encoding not in self._SUPPORTED:
            raise ValueError(f"encoding must be one of {self._SUPPORTED}, got {encoding!r}")
        self._encoding = encoding

    @property
    def query_param(self) -> str:
        """Return encoding string for WS URL query parameter."""
        return self._encoding

    def encode(self, obj: dict[str, Any]) -> str | bytes:
        """Serialize dict to wire format.

        Args:
            obj: Dict to encode.

        Returns:
            JSON string or msgpack bytes.
        """
        if self._encoding == "json":
            return json.dumps(obj)
        try:
            import msgpack  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "msgpack is required for msgpack encoding: pip install msgpack"
            ) from exc
        return msgpack.packb(obj, use_bin_type=True)  # type: ignore[no-any-return]

    def decode(self, data: str | bytes) -> dict[str, Any]:
        """Deserialize wire data to dict.

        Args:
            data: JSON string or msgpack bytes from server.

        Returns:
            Decoded dict.

        Raises:
            DnseStreamProtocolError: If data cannot be decoded.
        """
        try:
            if self._encoding == "json":
                return json.loads(data)  # type: ignore[arg-type]
            try:
                import msgpack  # type: ignore[import-untyped]
            except ImportError as exc:
                raise ImportError(
                    "msgpack is required for msgpack decoding: pip install msgpack"
                ) from exc
            return msgpack.unpackb(data, raw=False)  # type: ignore[no-any-return]
        except (json.JSONDecodeError, Exception) as exc:
            raise DnseStreamProtocolError(f"Failed to decode message: {exc}") from exc
