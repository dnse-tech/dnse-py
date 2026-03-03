"""Authentication and OTP models for DNSE SDK."""

from __future__ import annotations

from dnse.models.base import DnseBaseModel


class TwoFARequest(DnseBaseModel):
    """Request body for OTP verification (trading token retrieval)."""

    otp_type: str  # e.g. "email_otp"
    passcode: str


class TwoFAResponse(DnseBaseModel):
    """Response from the OTP verification endpoint."""

    trading_token: str  # camelCase: "tradingToken"
