"""Tests for order-related models."""

from dnse.models.orders import (
    GetOrdersResponse,
    OrderHistoryResponse,
    OrderItem,
    PlaceOrderRequest,
    PlaceOrderResponse,
    UpdateOrderRequest,
)


def test_place_order_request_creation():
    """PlaceOrderRequest can be created with required fields."""
    req = PlaceOrderRequest(
        account_no="123",
        symbol="HPG",
        side="NB",
        order_type="LO",
        quantity=100,
        price=27000.0,
    )
    assert req.account_no == "123"
    assert req.symbol == "HPG"
    assert req.side == "NB"
    assert req.order_type == "LO"
    assert req.quantity == 100
    assert req.price == 27000.0


def test_place_order_request_model_dump_by_alias():
    """PlaceOrderRequest.model_dump(by_alias=True) produces camelCase."""
    req = PlaceOrderRequest(
        account_no="456",
        symbol="MBB",
        side="NS",
        order_type="ATO",
        quantity=50,
        price=25000.0,
        loan_package_id=1,
        order_category="NORMAL",
        market_type="STOCK",
    )
    dumped = req.model_dump(by_alias=True)
    assert dumped["accountNo"] == "456"
    assert dumped["symbol"] == "MBB"
    assert dumped["side"] == "NS"
    assert dumped["orderType"] == "ATO"
    assert dumped["quantity"] == 50
    assert dumped["price"] == 25000.0
    assert dumped["loanPackageId"] == 1
    assert dumped["orderCategory"] == "NORMAL"
    assert dumped["marketType"] == "STOCK"


def test_place_order_request_optional_fields():
    """PlaceOrderRequest works with minimal fields."""
    req = PlaceOrderRequest(
        account_no="789",
        symbol="VNM",
        side="NB",
        order_type="MOK",
        quantity=10,
    )
    assert req.price is None
    assert req.loan_package_id is None


def test_order_item_creation():
    """OrderItem can be created with various fields."""
    item = OrderItem(
        id=1,
        account_no="123",
        symbol="HPG",
        side="NB",
        order_type="LO",
        order_status="New",
        quantity=100,
        price=27000.0,
    )
    assert item.id == 1
    assert item.account_no == "123"
    assert item.order_status == "New"


def test_order_item_model_validate_camel_case():
    """OrderItem.model_validate with camelCase JSON."""
    item = OrderItem.model_validate(
        {
            "id": 42,
            "accountNo": "456",
            "symbol": "MBB",
            "side": "NS",
            "orderType": "ATO",
            "orderStatus": "Filled",
            "quantity": 50,
            "fillQuantity": 50,
            "leaveQuantity": 0,
            "price": 25000.0,
            "averagePrice": 25000.0,
        }
    )
    assert item.id == 42
    assert item.account_no == "456"
    assert item.order_status == "Filled"
    assert item.fill_quantity == 50
    assert item.leave_quantity == 0
    assert item.average_price == 25000.0


def test_place_order_response_creation():
    """PlaceOrderResponse can be created with order details."""
    resp = PlaceOrderResponse(
        id=99,
        account_no="123",
        symbol="HPG",
        side="NB",
        order_type="LO",
        order_status="New",
        quantity=100,
    )
    assert resp.id == 99
    assert resp.account_no == "123"
    assert resp.order_status == "New"


def test_get_orders_response_creation():
    """GetOrdersResponse can be created with orders list."""
    orders = [
        OrderItem(id=1, symbol="HPG"),
        OrderItem(id=2, symbol="MBB"),
    ]
    resp = GetOrdersResponse(orders=orders)
    assert len(resp.orders) == 2


def test_get_orders_response_empty_list():
    """GetOrdersResponse.model_validate with empty orders."""
    resp = GetOrdersResponse.model_validate({"orders": []})
    assert resp.orders == []


def test_get_orders_response_model_validate_camel_case():
    """GetOrdersResponse.model_validate with camelCase JSON."""
    resp = GetOrdersResponse.model_validate(
        {
            "orders": [
                {"id": 1, "accountNo": "123", "symbol": "HPG"},
                {"id": 2, "accountNo": "456", "symbol": "MBB"},
            ]
        }
    )
    assert len(resp.orders) == 2
    assert resp.orders[0].symbol == "HPG"


def test_update_order_request_with_price():
    """UpdateOrderRequest with only price."""
    req = UpdateOrderRequest(price=27500.0)
    dumped = req.model_dump(by_alias=True, exclude_none=True)
    assert dumped == {"price": 27500.0}
    assert "quantity" not in dumped


def test_update_order_request_with_quantity():
    """UpdateOrderRequest with only quantity."""
    req = UpdateOrderRequest(quantity=200)
    dumped = req.model_dump(by_alias=True, exclude_none=True)
    assert dumped == {"quantity": 200}
    assert "price" not in dumped


def test_update_order_request_with_both():
    """UpdateOrderRequest with both price and quantity."""
    req = UpdateOrderRequest(price=28000.0, quantity=150)
    dumped = req.model_dump(by_alias=True, exclude_none=True)
    assert dumped["price"] == 28000.0
    assert dumped["quantity"] == 150


def test_update_order_request_empty():
    """UpdateOrderRequest with no fields excludes all keys."""
    req = UpdateOrderRequest()
    dumped = req.model_dump(by_alias=True, exclude_none=True)
    assert dumped == {}


def test_order_history_response_creation():
    """OrderHistoryResponse can be created with data list."""
    items = [
        OrderItem(id=1, symbol="HPG"),
        OrderItem(id=2, symbol="MBB"),
    ]
    resp = OrderHistoryResponse(data=items, total=2, page_index=1)
    assert len(resp.data) == 2
    assert resp.total == 2
    assert resp.page_index == 1


def test_order_history_response_model_validate():
    """OrderHistoryResponse.model_validate with camelCase JSON."""
    resp = OrderHistoryResponse.model_validate(
        {
            "data": [
                {"id": 10, "symbol": "HPG"},
                {"id": 11, "symbol": "MBB"},
            ],
            "total": 100,
            "pageIndex": 1,
            "pageNumber": 1,
            "pageSize": 2,
        }
    )
    assert len(resp.data) == 2
    assert resp.total == 100
    assert resp.page_index == 1
    assert resp.page_number == 1
    assert resp.page_size == 2
