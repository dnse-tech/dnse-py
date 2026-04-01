"""Tests for market data models."""

import pytest

from dnse.models.market import (
    BoardId,
    MarketId,
    ProductGrpId,
    SecurityDefinition,
    SecurityGroupId,
    SecurityStatus,
    Trade,
)
from dnse.resources.market import _parse_trade_list


def test_security_definition_creation():
    """SecurityDefinition can be created with various fields."""
    secdef = SecurityDefinition(
        symbol="HPG",
        market_id=6,  # MarketId.STO (HOSE)
        basic_price=27600,
        ceiling_price=30360,
        floor_price=24840,
    )
    assert secdef.symbol == "HPG"
    assert secdef.market_id == MarketId.STO
    assert secdef.basic_price == 27600


def test_security_definition_model_validate_camel_case():
    """SecurityDefinition.model_validate with camelCase JSON including enum fields."""
    secdef = SecurityDefinition.model_validate(
        {
            "symbol": "MBB",
            "marketId": 7,  # MarketId.STX (HNX)
            "boardId": "G1",
            "isin": "VN0000000001",
            "productGrpId": 8,  # ProductGrpId.STX
            "securityGroupId": 7,  # SecurityGroupId.ST (stock)
            "securityStatus": 2,  # SecurityStatus.NO_HALT
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
    assert secdef.market_id == MarketId.STX
    assert secdef.board_id == BoardId.ROUND_LOT
    assert secdef.isin == "VN0000000001"
    assert secdef.product_grp_id == ProductGrpId.STX
    assert secdef.security_group_id == SecurityGroupId.ST
    assert secdef.security_status == SecurityStatus.NO_HALT
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


def test_security_definition_unknown_int_codes_fallback():
    """Unknown int codes fall back to raw int without raising."""
    secdef = SecurityDefinition(
        market_id=99, product_grp_id=99, security_group_id=99, security_status=99
    )
    assert secdef.market_id == 99
    assert isinstance(secdef.market_id, int)
    assert secdef.product_grp_id == 99
    assert secdef.security_group_id == 99
    assert secdef.security_status == 99


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


# --- MarketId enum tests ---


def test_market_id_values():
    """MarketId enum values match server codes."""
    assert MarketId.UNSPECIFIED == 0
    assert MarketId.DVX == 3
    assert MarketId.HCX == 4
    assert MarketId.STO == 6
    assert MarketId.STX == 7
    assert MarketId.UPX == 8


def test_market_id_coercion_from_int():
    """SecurityDefinition coerces int market_id to MarketId enum."""
    secdef = SecurityDefinition(market_id=6)
    assert secdef.market_id == MarketId.STO
    assert isinstance(secdef.market_id, MarketId)


def test_market_id_coercion_from_str_int():
    """SecurityDefinition coerces string-encoded int market_id to MarketId enum."""
    secdef = SecurityDefinition.model_validate({"marketId": "6"})
    assert secdef.market_id == MarketId.STO


# --- ProductGrpId enum tests ---


def test_product_grp_id_values():
    """ProductGrpId enum values match server codes."""
    assert ProductGrpId.UNSPECIFIED == 0
    assert ProductGrpId.FBX == 3
    assert ProductGrpId.FIO == 4
    assert ProductGrpId.HCX == 5
    assert ProductGrpId.STO == 7
    assert ProductGrpId.STX == 8
    assert ProductGrpId.UPX == 9


def test_product_grp_id_coercion():
    """SecurityDefinition coerces product_grp_id to ProductGrpId enum."""
    secdef = SecurityDefinition(product_grp_id=7)
    assert secdef.product_grp_id == ProductGrpId.STO


# --- SecurityGroupId enum tests ---


def test_security_group_id_values():
    """SecurityGroupId enum values match server codes."""
    assert SecurityGroupId.UNSPECIFIED == 0
    assert SecurityGroupId.BS == 1
    assert SecurityGroupId.EF == 2
    assert SecurityGroupId.EW == 3
    assert SecurityGroupId.FU == 4
    assert SecurityGroupId.SR == 6
    assert SecurityGroupId.ST == 7


def test_security_group_id_coercion():
    """SecurityDefinition coerces security_group_id to SecurityGroupId enum."""
    secdef = SecurityDefinition(security_group_id=7)
    assert secdef.security_group_id == SecurityGroupId.ST


# --- SecurityStatus enum tests ---


def test_security_status_values():
    """SecurityStatus enum values match server codes."""
    assert SecurityStatus.HALT == 1
    assert SecurityStatus.NO_HALT == 2


def test_security_status_coercion():
    """SecurityDefinition coerces security_status to SecurityStatus enum."""
    secdef = SecurityDefinition(security_status=1)
    assert secdef.security_status == SecurityStatus.HALT
    secdef2 = SecurityDefinition(security_status=2)
    assert secdef2.security_status == SecurityStatus.NO_HALT


# --- Trade model tests ---


def test_trade_creation():
    """Trade can be created with typed fields and enum coercion."""
    trade = Trade(
        symbol="HPG",
        market_id=6,
        board_id="G1",
        match_price=27.5,
        match_qtty=100,
        side="BUY",
    )
    assert trade.symbol == "HPG"
    assert trade.market_id == MarketId.STO
    assert trade.board_id == BoardId.ROUND_LOT
    assert trade.match_price == 27.5
    assert trade.match_qtty == 100
    assert trade.side == "BUY"


def test_trade_model_validate_camel_case():
    """Trade.model_validate with camelCase JSON."""
    trade = Trade.model_validate(
        {
            "marketId": 7,
            "boardId": "G1",
            "isin": "VN0000000001",
            "symbol": "MBB",
            "matchPrice": 25.0,
            "matchQtty": 200,
            "side": "SELL",
            "avgPrice": 24.8,
            "totalVolumeTraded": 500000,
            "grossTradeAmount": 12400000.0,
            "highestPrice": 26.0,
            "lowestPrice": 24.0,
            "openPrice": 24.5,
            "time": "14:30:00",
        }
    )
    assert trade.symbol == "MBB"
    assert trade.market_id == MarketId.STX
    assert trade.board_id == BoardId.ROUND_LOT
    assert trade.match_price == 25.0
    assert trade.side == "SELL"
    assert trade.avg_price == 24.8
    assert trade.total_volume_traded == 500000
    assert trade.time == "14:30:00"


def test_trade_minimal():
    """Trade works with minimal fields."""
    trade = Trade.model_validate({"symbol": "VNM"})
    assert trade.symbol == "VNM"
    assert trade.market_id is None
    assert trade.match_price is None


def test_trade_all_optional():
    """Trade with all optional fields (empty constructor)."""
    trade = Trade()
    assert trade.symbol is None
    assert trade.market_id is None
    assert trade.match_price is None


def test_trade_unknown_enums_fallback():
    """Unknown enum values fall back to raw type without raising."""
    trade = Trade(market_id=99, board_id="UNKNOWN")
    assert trade.market_id == 99
    assert isinstance(trade.market_id, int)
    assert trade.board_id == "UNKNOWN"
    assert isinstance(trade.board_id, str)


def test_trade_board_id_coercion():
    """Trade coerces 'G1' string to BoardId.ROUND_LOT."""
    trade = Trade(board_id="G1")
    assert trade.board_id == BoardId.ROUND_LOT
    assert isinstance(trade.board_id, BoardId)


def test_trade_market_id_coercion():
    """Trade coerces int 6 to MarketId.STO."""
    trade = Trade(market_id=6)
    assert trade.market_id == MarketId.STO
    assert isinstance(trade.market_id, MarketId)


# --- _parse_trade_list helper tests ---


def test_parse_trade_list_valid():
    """_parse_trade_list unwraps trades dict correctly."""
    body = {
        "trades": [
            {"symbol": "HPG", "matchPrice": 27.5},
            {"symbol": "MBB", "matchPrice": 25.0},
        ]
    }
    result = _parse_trade_list(body)
    assert len(result) == 2
    assert result[0].symbol == "HPG"
    assert result[1].symbol == "MBB"


def test_parse_trade_list_empty():
    """_parse_trade_list returns empty list for empty trades array."""
    assert _parse_trade_list({"trades": []}) == []


def test_parse_trade_list_missing_key():
    """_parse_trade_list returns empty list when 'trades' key missing."""
    assert _parse_trade_list({"other": "data"}) == []


def test_parse_trade_list_non_dict():
    """_parse_trade_list returns empty list for non-dict body."""
    assert _parse_trade_list("not a dict") == []
    assert _parse_trade_list([1, 2, 3]) == []


def test_parse_trade_list_trades_not_a_list():
    """_parse_trade_list returns empty list when trades value is not a list."""
    assert _parse_trade_list({"trades": "not_a_list"}) == []
    assert _parse_trade_list({"trades": 123}) == []


# --- Import verification ---


def test_trade_import_from_models():
    """Trade can be imported from dnse.models."""
    from dnse.models import Trade as TradeImport

    assert TradeImport is Trade
