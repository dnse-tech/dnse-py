"""Order-related request and response models for DNSE SDK."""

from __future__ import annotations

from dnse.models.base import DnseBaseModel


class PlaceOrderRequest(DnseBaseModel):
    """Request body for placing a new order (POST /accounts/orders)."""

    account_no: str
    symbol: str
    side: str           # "NB" (buy) | "NS" (sell)
    order_type: str     # "LO" | "ATO" | "ATC" | "MTL" | "MOK" | "MAK"
    quantity: int
    price: float | None = None          # required for LO
    loan_package_id: int | None = None
    order_category: str | None = None   # e.g. "NORMAL"
    market_type: str | None = None      # e.g. "STOCK"


class OrderItem(DnseBaseModel):
    """A single order entry (from list or history)."""

    id: int | None = None
    account_no: str | None = None
    symbol: str | None = None
    side: str | None = None
    order_type: str | None = None
    order_status: str | None = None
    order_category: str | None = None
    market_type: str | None = None
    quantity: int | None = None
    fill_quantity: int | None = None
    leave_quantity: int | None = None
    canceled_quantity: int | None = None
    price: float | None = None
    average_price: float | None = None
    price_secure: float | None = None
    loan_package_id: int | None = None
    trans_date: str | None = None
    created_date: str | None = None
    modified_date: str | None = None


class PlaceOrderResponse(DnseBaseModel):
    """Response from POST /accounts/orders."""

    id: int | None = None
    account_no: str | None = None
    symbol: str | None = None
    side: str | None = None
    order_type: str | None = None
    order_status: str | None = None
    order_category: str | None = None
    market_type: str | None = None
    quantity: int | None = None
    fill_quantity: int | None = None
    leave_quantity: int | None = None
    canceled_quantity: int | None = None
    price: float | None = None
    average_price: float | None = None
    loan_package_id: int | None = None
    trans_date: str | None = None
    created_date: str | None = None
    modified_date: str | None = None


class GetOrdersResponse(DnseBaseModel):
    """Response from GET /accounts/{accountNo}/orders."""

    orders: list[OrderItem] = []


class UpdateOrderRequest(DnseBaseModel):
    """Request body for modifying an existing order."""

    quantity: int | None = None
    price: float | None = None


class OrderHistoryResponse(DnseBaseModel):
    """Response from GET /accounts/{accountNo}/orders/history."""

    data: list[OrderItem] = []
    total: int | None = None
    page_index: int | None = None
    page_number: int | None = None
    page_size: int | None = None
