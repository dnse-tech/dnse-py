"""Tests for market data models."""

from dnse.models.market import SecurityDefinition


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
    """SecurityDefinition.model_validate with camelCase JSON."""
    secdef = SecurityDefinition.model_validate(
        {
            "symbol": "MBB",
            "marketId": "STO",
            "boardId": "HOSE",
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
    assert secdef.board_id == "HOSE"
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
