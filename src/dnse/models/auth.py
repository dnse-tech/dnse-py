"""Authentication and OTP models for DNSE SDK."""

from __future__ import annotations

from typing import Literal

from dnse.models.base import DnseBaseModel

OtpType = Literal["email_otp", "smart_otp"]


class TwoFARequest(DnseBaseModel):
    """Request body for OTP verification (trading token retrieval)."""

    otp_type: OtpType
    passcode: str


class TwoFAResponse(DnseBaseModel):
    """Response from the OTP verification endpoint."""

    trading_token: str  # camelCase: "tradingToken"
