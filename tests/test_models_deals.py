"""Tests for deal (position) models."""

from dnse.models.deals import DealItem, DealsResponse


def test_deal_item_creation():
    """DealItem can be created with various fields."""
    item = DealItem(
        id=1,
        account_no="123",
        symbol="HPG",
        side="BUY",
        status="OPEN",
        open_quantity=100,
        cost_price=27000.0,
        market_price=28000.0,
    )
    assert item.id == 1
    assert item.symbol == "HPG"
    assert item.side == "BUY"
    assert item.status == "OPEN"


def test_deal_item_model_validate_camel_case():
    """DealItem.model_validate with camelCase JSON."""
    item = DealItem.model_validate(
        {
            "id": 42,
            "accountNo": "456",
            "symbol": "MBB",
            "side": "SELL",
            "status": "CLOSED",
            "openQuantity": 50,
            "tradeQuantity": 50,
            "accumulateQuantity": 100,
            "closedQuantity": 50,
            "overNightQuantity": 0,
            "costPrice": 25000.0,
            "marketPrice": 26000.0,
            "breakEvenPrice": 25500.0,
        }
    )
    assert item.id == 42
    assert item.account_no == "456"
    assert item.symbol == "MBB"
    assert item.side == "SELL"
    assert item.open_quantity == 50
    assert item.trade_quantity == 50
    assert item.break_even_price == 25500.0


def test_deal_item_optional_fields():
    """DealItem works with minimal fields."""
    item = DealItem.model_validate({"id": 1, "symbol": "VNM"})
    assert item.id == 1
    assert item.symbol == "VNM"
    assert item.status is None
    assert item.cost_price is None


def test_deals_response_creation():
    """DealsResponse can be created with deals list."""
    deals = [
        DealItem(id=1, symbol="HPG"),
        DealItem(id=2, symbol="MBB"),
    ]
    resp = DealsResponse(deals=deals, total=2, page_index=1)
    assert len(resp.deals) == 2
    assert resp.total == 2


def test_deals_response_empty_list():
    """DealsResponse.model_validate with empty deals."""
    resp = DealsResponse.model_validate({"deals": []})
    assert resp.deals == []


def test_deals_response_model_validate_camel_case():
    """DealsResponse.model_validate with camelCase JSON."""
    resp = DealsResponse.model_validate(
        {
            "deals": [
                {
                    "id": 1,
                    "accountNo": "123",
                    "symbol": "HPG",
                    "side": "BUY",
                },
                {
                    "id": 2,
                    "accountNo": "456",
                    "symbol": "MBB",
                    "side": "SELL",
                },
            ],
            "total": 100,
            "pageIndex": 1,
            "pageNumber": 1,
            "pageSize": 2,
        }
    )
    assert len(resp.deals) == 2
    assert resp.total == 100
    assert resp.page_index == 1
    assert resp.page_number == 1
    assert resp.page_size == 2


def test_deals_response_pagination_fields():
    """DealsResponse handles pagination fields correctly."""
    resp = DealsResponse.model_validate(
        {
            "deals": [],
            "total": 500,
            "pageIndex": 3,
            "pageNumber": 3,
            "pageSize": 100,
        }
    )
    assert resp.total == 500
    assert resp.page_index == 3
    assert resp.page_number == 3
    assert resp.page_size == 100
