"""Registration resource: OTP flow for obtaining a trading token."""

from __future__ import annotations

from typing import TYPE_CHECKING

from dnse._http import handle_response
from dnse.models.auth import OtpType, TwoFARequest, TwoFAResponse

if TYPE_CHECKING:
    from dnse._base_client import BaseClient
    from dnse.async_client import AsyncDnseClient


class RegistrationResource:
    """Sync resource for OTP-based trading token acquisition."""

    def __init__(self, client: BaseClient) -> None:
        """Initialize with a sync client reference.

        Args:
            client: Parent DnseClient instance.
        """
        self._client = client

    def send_otp(self) -> None:
        """Request an OTP email from the server.

        Sends POST /registration/send-email-otp.
        The server emails an OTP to the registered address.
        """
        path = "/registration/send-email-otp"
        headers = self._client._request_headers("POST", path)
        response = self._client._send("POST", path, headers=headers)
        handle_response(
            response.status_code,
            response.text,
            dict(response.headers),
            trading_token_set=self._client._trading_token is not None,
        )

    def verify_otp(self, otp: str, *, otp_type: OtpType = "email_otp") -> str:
        """Verify OTP and obtain a trading token.

        Sends POST /registration/trading-token, stores the returned token
        on the client, and returns it for caller convenience.

        Args:
            otp: The OTP code received via email.
            otp_type: OTP type string (default "email_otp").

        Returns:
            The trading token string.
        """
        path = "/registration/trading-token"
        body = TwoFARequest(otp_type=otp_type, passcode=otp)
        headers = self._client._request_headers("POST", path)
        response = self._client._send(
            "POST",
            path,
            headers=headers,
            json=body.model_dump(by_alias=True),
        )
        result = self._client._parse(response, TwoFAResponse)
        self._client.set_trading_token(result.trading_token)
        return result.trading_token


class AsyncRegistrationResource:
    """Async resource for OTP-based trading token acquisition."""

    def __init__(self, client: AsyncDnseClient) -> None:
        """Initialize with an async client reference.

        Args:
            client: Parent AsyncDnseClient instance.
        """
        self._client = client

    async def send_otp(self) -> None:
        """Request an OTP email from the server (async).

        Sends POST /registration/send-email-otp.
        """
        path = "/registration/send-email-otp"
        headers = self._client._request_headers("POST", path)
        response = await self._client._async_send("POST", path, headers=headers)
        handle_response(
            response.status_code,
            response.text,
            dict(response.headers),
            trading_token_set=self._client._trading_token is not None,
        )

    async def verify_otp(self, otp: str, *, otp_type: str = "email_otp") -> str:
        """Verify OTP and obtain a trading token (async).

        Args:
            otp: The OTP code received via email.
            otp_type: OTP type string (default "email_otp").

        Returns:
            The trading token string.
        """
        path = "/registration/trading-token"
        body = TwoFARequest(otp_type=otp_type, passcode=otp)
        headers = self._client._request_headers("POST", path)
        response = await self._client._async_send(
            "POST",
            path,
            headers=headers,
            json=body.model_dump(by_alias=True),
        )
        result = self._client._parse(response, TwoFAResponse)
        self._client.set_trading_token(result.trading_token)
        return result.trading_token
