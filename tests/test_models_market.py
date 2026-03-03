"""Tests for market data models."""

import pytest

from dnse.models.market import BoardId, SecurityDefinition


def test_security_definition_creation():
    """SecurityDefinition can be created with various fields."""
    secdef = SecurityDefinition(
        symbol="HPG",
        market_id="STO",
        basic_price=27600,
        ceiling_price=30360,
        floor_price=24840,
    )
    assert secdef.symbol == "HPG"
    assert secdef.market_id == "STO"
    assert secdef.basic_price == 27600


def test_security_definition_model_validate_camel_case():
    """SecurityDefinition.model_validate with camelCase JSON including BoardId."""
    secdef = SecurityDefinition.model_validate(
        {
            "symbol": "MBB",
            "marketId": "STO",
            "boardId": "G1",
            "isin": "VN0000000001",
            "productGrpId": "STOCK",
            "securityGroupId": "SG1",
            "securityStatus": "TRADING",
            "symbolAdminStatusCode": "ACTIVE",
            "symbolTradingMethodStatusCode": "NORMAL",
            "symbolTradingSanctionStatusCode": "NONE",
            "basicPrice": 25000,
            "ceilingPrice": 27500,
            "floorPrice": 22500,
            "openInterestQuantity": 1000000,
        }
    )
    assert secdef.symbol == "MBB"
    assert secdef.market_id == "STO"
    assert secdef.board_id == "G1"  # kept as raw string from server
    assert secdef.isin == "VN0000000001"
    assert secdef.product_grp_id == "STOCK"
    assert secdef.basic_price == 25000
    assert secdef.ceiling_price == 27500
    assert secdef.floor_price == 22500


def test_security_definition_minimal():
    """SecurityDefinition works with minimal fields."""
    secdef = SecurityDefinition.model_validate({"symbol": "VNM"})
    assert secdef.symbol == "VNM"
    assert secdef.market_id is None
    assert secdef.basic_price is None


def test_security_definition_all_optional():
    """SecurityDefinition with all optional fields."""
    secdef = SecurityDefinition()
    assert secdef.symbol is None
    assert secdef.market_id is None
    assert secdef.basic_price is None


# --- BoardId enum tests ---


def test_board_id_values_match_server_codes():
    """BoardId enum values are the server short codes."""
    assert BoardId.ALL.value == "AL"
    assert BoardId.ROUND_LOT.value == "G1"
    assert BoardId.AFTER_HOURS_PLO.value == "G3"
    assert BoardId.ODD_LOT.value == "G4"
    assert BoardId.PT_ROUND_LOT_MORNING.value == "T1"
    assert BoardId.PT_ROUND_LOT_AFTERNOON.value == "T3"
    assert BoardId.PT_ODD_LOT_MORNING.value == "T4"
    assert BoardId.PT_ODD_LOT_AFTERNOON.value == "T6"


def test_board_id_is_str_enum():
    """BoardId members compare equal to their string values."""
    assert BoardId.ALL == "AL"
    assert BoardId.ROUND_LOT == "G1"


def test_board_id_lookup_from_server_code():
    """BoardId can be constructed from server short code."""
    assert BoardId("AL") == BoardId.ALL
    assert BoardId("G1") == BoardId.ROUND_LOT


def test_board_id_unknown_code_raises():
    """Unknown server codes raise ValueError."""
    with pytest.raises(ValueError):
        BoardId("UNKNOWN")
