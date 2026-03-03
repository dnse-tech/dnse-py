"""Tests for WebSocket HMAC auth message builder."""

import hashlib
import hmac
import time

from dnse.stream._stream_auth import build_auth_message


def test_build_auth_message_keys():
    msg = build_auth_message("key123", "secret456")
    assert set(msg.keys()) == {"action", "api_key", "signature", "timestamp", "nonce"}


def test_build_auth_message_action():
    assert build_auth_message("key123", "secret456")["action"] == "auth"


def test_build_auth_message_api_key():
    assert build_auth_message("mykey", "mysecret")["api_key"] == "mykey"


def test_build_auth_message_signature_is_valid_hex():
    sig = str(build_auth_message("key123", "secret456")["signature"])
    assert len(sig) == 64
    assert all(c in "0123456789abcdef" for c in sig)


def test_build_auth_message_signature_matches_hmac():
    api_key, api_secret = "testkey", "testsecret"
    msg = build_auth_message(api_key, api_secret)
    payload = f"{api_key}:{msg['timestamp']}:{msg['nonce']}"
    expected = hmac.new(api_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    assert msg["signature"] == expected


def test_build_auth_message_timestamp_is_recent():
    before = int(time.time()) - 2
    msg = build_auth_message("k", "s")
    assert before <= int(msg["timestamp"]) <= int(time.time()) + 2  # type: ignore[arg-type]


def test_build_auth_message_nonce_is_microsecond_precision():
    msg = build_auth_message("k", "s")
    assert int(msg["nonce"]) > int(msg["timestamp"])  # type: ignore[arg-type]


def test_build_auth_message_secret_not_in_payload():
    secret = "supersecret"
    msg = build_auth_message("k", secret)
    for v in msg.values():
        assert secret not in str(v)
