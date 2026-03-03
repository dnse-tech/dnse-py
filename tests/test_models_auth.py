"""Tests for auth models: TwoFARequest and TwoFAResponse."""

from dnse.models.auth import TwoFARequest, TwoFAResponse


def test_two_fa_request_creation():
    """TwoFARequest can be created with otp_type and passcode."""
    req = TwoFARequest(otp_type="email_otp", passcode="123456")
    assert req.otp_type == "email_otp"
    assert req.passcode == "123456"


def test_two_fa_request_model_dump_by_alias():
    """TwoFARequest.model_dump(by_alias=True) produces camelCase keys."""
    req = TwoFARequest(otp_type="email_otp", passcode="123456")
    dumped = req.model_dump(by_alias=True)
    assert "otpType" in dumped
    assert dumped["otpType"] == "email_otp"
    assert "passcode" in dumped
    assert dumped["passcode"] == "123456"


def test_two_fa_request_model_dump_without_alias():
    """TwoFARequest.model_dump() produces snake_case keys."""
    req = TwoFARequest(otp_type="email_otp", passcode="123456")
    dumped = req.model_dump()
    assert "otp_type" in dumped
    assert dumped["otp_type"] == "email_otp"
    assert "passcode" in dumped


def test_two_fa_response_creation():
    """TwoFAResponse can be created with trading_token."""
    resp = TwoFAResponse(trading_token="abc123def456")
    assert resp.trading_token == "abc123def456"


def test_two_fa_response_model_validate_camel_case():
    """TwoFAResponse.model_validate with camelCase keys works."""
    resp = TwoFAResponse.model_validate({"tradingToken": "abc123"})
    assert resp.trading_token == "abc123"


def test_two_fa_response_model_validate_snake_case():
    """TwoFAResponse.model_validate with snake_case keys works (populate_by_name=True)."""
    resp = TwoFAResponse.model_validate({"trading_token": "xyz789"})
    assert resp.trading_token == "xyz789"


def test_two_fa_response_model_dump_by_alias():
    """TwoFAResponse.model_dump(by_alias=True) produces camelCase."""
    resp = TwoFAResponse(trading_token="token123")
    dumped = resp.model_dump(by_alias=True)
    assert "tradingToken" in dumped
    assert dumped["tradingToken"] == "token123"
