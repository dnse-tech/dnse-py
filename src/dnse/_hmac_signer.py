"""Stateless HMAC-SHA256 request signer for DNSE Open API."""

from __future__ import annotations

import base64
import hashlib
import hmac
import urllib.parse
import uuid
from datetime import datetime, timezone


def _rfc2822_now() -> str:
    """Return current UTC time in RFC 2822 format."""
    return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")


def build_signature_headers(
    method: str,
    path: str,
    api_key: str,
    api_secret: str,
    *,
    date_header: str = "date",
    use_nonce: bool = True,
) -> dict[str, str]:
    """Build HMAC-SHA256 auth headers for a single request.

    Args:
        method: HTTP method (e.g. "GET", "POST").
        path: URL path including query string (e.g. "/accounts").
        api_key: API key identifier.
        api_secret: API secret for HMAC signing.
        date_header: Header name for the date ("date" or "x-aux-date").
        use_nonce: Whether to include a uuid4 nonce in the signature.

    Returns:
        Dict with x-api-key, date header, X-Signature, and optional nonce.
    """
    date_value = _rfc2822_now()
    nonce = uuid.uuid4().hex if use_nonce else None

    signed_headers = f"(request-target) {date_header}"
    parts = [
        f"(request-target): {method.lower()} {path}",
        f"{date_header}: {date_value}",
    ]
    if nonce:
        parts.append(f"nonce: {nonce}")
        signed_headers += " nonce"

    sig_string = "\n".join(parts)
    raw_sig = hmac.new(api_secret.encode(), sig_string.encode(), hashlib.sha256).digest()
    sig = urllib.parse.quote(base64.b64encode(raw_sig).decode(), safe="")

    sig_header = (
        f'Signature keyId="{api_key}",algorithm="hmac-sha256",'
        f'headers="{signed_headers}",signature="{sig}"'
    )
    if nonce:
        sig_header += f',nonce="{nonce}"'

    headers: dict[str, str] = {
        "x-api-key": api_key,
        date_header: date_value,
        "X-Signature": sig_header,
    }
    if nonce:
        headers["nonce"] = nonce
    return headers
