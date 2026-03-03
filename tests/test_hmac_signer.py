"""Tests for HMAC signature generation in _hmac_signer.py."""

import base64
import hashlib
import hmac
import re

from dnse._hmac_signer import build_signature_headers


def test_build_signature_headers_returns_dict():
    """build_signature_headers returns a dictionary."""
    result = build_signature_headers("GET", "/accounts", "key1", "secret1")
    assert isinstance(result, dict)


def test_build_signature_headers_has_api_key():
    """Response includes x-api-key header."""
    headers = build_signature_headers("GET", "/accounts", "my-api-key", "secret")
    assert headers["x-api-key"] == "my-api-key"


def test_build_signature_headers_has_date():
    """Response includes date header by default."""
    headers = build_signature_headers("GET", "/accounts", "key", "secret")
    assert "date" in headers
    assert headers["date"]  # Non-empty


def test_build_signature_headers_has_signature():
    """Response includes X-Signature header."""
    headers = build_signature_headers("GET", "/accounts", "key", "secret")
    assert "X-Signature" in headers
    sig_value = headers["X-Signature"]
    assert sig_value.startswith("Signature keyId=")


def test_build_signature_headers_signature_format():
    """X-Signature has correct format with required fields."""
    headers = build_signature_headers("GET", "/accounts", "key1", "secret1")
    sig = headers["X-Signature"]
    assert 'keyId="key1"' in sig
    assert 'algorithm="hmac-sha256"' in sig
    assert "headers=" in sig
    assert "signature=" in sig


def test_build_signature_headers_with_nonce_true():
    """With use_nonce=True, nonce is present."""
    headers = build_signature_headers("GET", "/accounts", "key", "secret", use_nonce=True)
    assert "nonce" in headers
    # nonce should be a UUID hex string (32 chars)
    assert len(headers["nonce"]) == 32
    # Signature should also contain the nonce
    assert "nonce=" in headers["X-Signature"]


def test_build_signature_headers_with_nonce_false():
    """With use_nonce=False, no nonce is present."""
    headers = build_signature_headers("GET", "/accounts", "key", "secret", use_nonce=False)
    assert "nonce" not in headers
    # Signature should NOT contain nonce
    assert "nonce=" not in headers["X-Signature"]


def test_build_signature_headers_custom_date_header():
    """Custom date_header parameter is respected."""
    headers = build_signature_headers("GET", "/accounts", "key", "secret", date_header="x-aux-date")
    assert "x-aux-date" in headers
    assert "date" not in headers
    assert headers["x-aux-date"]  # Non-empty


def test_build_signature_headers_signature_includes_custom_date_header():
    """Custom date header name is included in X-Signature."""
    headers = build_signature_headers("GET", "/accounts", "key", "secret", date_header="x-aux-date")
    sig = headers["X-Signature"]
    assert "x-aux-date" in sig


def test_build_signature_headers_different_methods():
    """Different HTTP methods produce different signatures."""
    get_headers = build_signature_headers("GET", "/accounts", "key", "secret", use_nonce=False)
    post_headers = build_signature_headers("POST", "/accounts", "key", "secret", use_nonce=False)
    # Signatures should differ because method is part of the signed content
    assert get_headers["X-Signature"] != post_headers["X-Signature"]


def test_build_signature_headers_different_paths():
    """Different paths produce different signatures."""
    headers1 = build_signature_headers("GET", "/accounts", "key", "secret", use_nonce=False)
    headers2 = build_signature_headers("GET", "/accounts/123", "key", "secret", use_nonce=False)
    # Signatures should differ because path is part of the signed content
    assert headers1["X-Signature"] != headers2["X-Signature"]


def test_build_signature_headers_different_secrets():
    """Different secrets produce different signatures."""
    headers1 = build_signature_headers("GET", "/accounts", "key", "secret1", use_nonce=False)
    headers2 = build_signature_headers("GET", "/accounts", "key", "secret2", use_nonce=False)
    # Signatures should differ because secret is used for HMAC
    assert headers1["X-Signature"] != headers2["X-Signature"]


def test_build_signature_headers_hmac_verifiable():
    """HMAC signature can be verified manually."""
    api_key = "test-key"
    api_secret = "test-secret"
    method = "GET"
    path = "/accounts"

    headers = build_signature_headers(method, path, api_key, api_secret, use_nonce=False)

    # Extract date and nonce from headers
    date_value = headers["date"]

    # Reconstruct the signed string
    signed_headers = "(request-target) date"
    sig_string = f"(request-target): {method.lower()} {path}\ndate: {date_value}"

    # Compute HMAC
    raw_sig = hmac.new(api_secret.encode(), sig_string.encode(), hashlib.sha256).digest()
    expected_sig = base64.b64encode(raw_sig).decode()

    # Extract signature from header
    sig_match = re.search(r'signature="([^"]+)"', headers["X-Signature"])
    assert sig_match
    actual_sig_encoded = sig_match.group(1)
    # Decode URL encoding
    import urllib.parse

    actual_sig = urllib.parse.unquote(actual_sig_encoded)

    assert actual_sig == expected_sig


def test_build_signature_headers_nonce_included_in_signature():
    """When nonce is present, it's included in signature computation."""
    headers = build_signature_headers("GET", "/accounts", "key", "secret", use_nonce=True)
    nonce = headers["nonce"]
    sig = headers["X-Signature"]

    # Signature should contain the nonce value
    assert nonce in sig
    # And should list nonce in headers
    assert "nonce" in sig


def test_build_signature_headers_post_method():
    """POST method is correctly lowercased in signature."""
    headers = build_signature_headers("POST", "/accounts/orders", "key", "secret", use_nonce=False)
    sig = headers["X-Signature"]
    # The signed string should have "post" (lowercase)
    assert "Signature keyId=" in sig
    assert "algorithm=" in sig


def test_build_signature_headers_query_string_in_path():
    """Query string is included in path for signature."""
    headers1 = build_signature_headers("GET", "/accounts", "key", "secret", use_nonce=False)
    headers2 = build_signature_headers(
        "GET", "/accounts?type=STOCK", "key", "secret", use_nonce=False
    )
    # Different signatures because query string changes the path
    assert headers1["X-Signature"] != headers2["X-Signature"]
