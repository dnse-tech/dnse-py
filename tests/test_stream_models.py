"""Tests for stream Pydantic v2 models and TYPE_MAP dispatch table."""

from dnse.stream.models import (
    TYPE_MAP,
    StreamAccountUpdate,
    StreamExpectedPrice,
    StreamOhlc,
    StreamOrder,
    StreamPosition,
    StreamQuote,
    StreamSecurityDef,
    StreamTrade,
    StreamTradeExtra,
)


def test_type_map_covers_all_t_values():
    assert set(TYPE_MAP.keys()) == {"t", "te", "q", "b", "e", "sd", "o", "p", "a"}


def test_stream_trade_validates_sample():
    obj = StreamTrade.model_validate({"symbol": "VIC", "price": 98.5, "volume": 1000})
    assert obj.symbol == "VIC" and obj.price == 98.5


def test_stream_trade_extra_camel_alias():
    obj = StreamTradeExtra.model_validate({"symbol": "VNM", "totalVolume": 50000})
    assert obj.total_volume == 50000


def test_stream_quote_validates():
    obj = StreamQuote.model_validate({"bidPrice": 95.0, "askPrice": 95.5, "askVolume": 300})
    assert obj.bid_price == 95.0 and obj.ask_volume == 300


def test_stream_ohlc_validates():
    obj = StreamOhlc.model_validate({"symbol": "VIC", "open": 95.0, "high": 99.0})
    assert obj.high == 99.0


def test_stream_expected_price_validates():
    obj = StreamExpectedPrice.model_validate({"symbol": "HPG", "price": 27.5})
    assert obj.price == 27.5


def test_stream_security_def_camel_alias():
    obj = StreamSecurityDef.model_validate({"ceiling": 110.0, "refPrice": 100.0})
    assert obj.ref_price == 100.0


def test_stream_order_validates():
    obj = StreamOrder.model_validate({"orderId": "ORD001", "status": "active"})
    assert obj.order_id == "ORD001" and obj.status == "active"


def test_stream_position_camel_alias():
    obj = StreamPosition.model_validate({"avgPrice": 80.0, "marketValue": 40000.0})
    assert obj.avg_price == 80.0


def test_stream_account_update_validates():
    obj = StreamAccountUpdate.model_validate({"accountNo": "ACC123", "equity": 105000.0})
    assert obj.account_no == "ACC123" and obj.equity == 105000.0


def test_optional_fields_default_to_none():
    obj = StreamTrade.model_validate({})
    assert obj.symbol is None and obj.price is None


def test_type_map_returns_correct_classes():
    assert TYPE_MAP["t"] is StreamTrade
    assert TYPE_MAP["q"] is StreamQuote
    assert TYPE_MAP["o"] is StreamOrder
    assert TYPE_MAP["a"] is StreamAccountUpdate
