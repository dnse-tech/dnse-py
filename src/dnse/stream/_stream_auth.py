"""WebSocket authentication message builder for DNSE streaming.

WS auth uses a different HMAC format than REST:
sig = HMAC-SHA256(api_secret, "{api_key}:{timestamp}:{nonce}").hexdigest()
"""

from __future__ import annotations

import hashlib
import hmac
import time

from dnse.stream.exceptions import DnseStreamAuthError


def build_auth_message(api_key: str, api_secret: str) -> dict[str, str | int]:
    """Build WebSocket authentication payload.

    Args:
        api_key: DNSE API key.
        api_secret: DNSE API secret (never included in returned payload).

    Returns:
        Dict with action, api_key, signature, timestamp, nonce.

    Raises:
        DnseStreamAuthError: If auth message cannot be constructed.
    """
    try:
        timestamp = int(time.time())
        nonce = int(time.time() * 1_000_000)
        payload = f"{api_key}:{timestamp}:{nonce}"
        sig = hmac.new(
            api_secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()
        return {
            "action": "auth",
            "api_key": api_key,
            "signature": sig,
            "timestamp": timestamp,
            "nonce": nonce,
        }
    except Exception as exc:
        raise DnseStreamAuthError(f"Failed to build auth message: {exc}") from exc
