"""Deal (position) response models for DNSE SDK."""

from __future__ import annotations

from dnse.models.base import DnseBaseModel


class DealItem(DnseBaseModel):
    """A single deal/position entry."""

    id: int | None = None
    account_no: str | None = None
    symbol: str | None = None
    side: str | None = None  # "BUY" | "SELL"
    status: str | None = None  # e.g. "OPEN"
    open_quantity: int | None = None
    trade_quantity: int | None = None
    accumulate_quantity: int | None = None
    closed_quantity: int | None = None
    over_night_quantity: int | None = None
    cost_price: float | None = None
    market_price: float | None = None
    break_even_price: float | None = None
    loan_package_id: int | None = None
    created_date: str | None = None
    modified_date: str | None = None


class DealsResponse(DnseBaseModel):
    """Response from GET /accounts/{accountNo}/positions."""

    deals: list[DealItem] = []
    page_index: int | None = None
    page_number: int | None = None
    page_size: int | None = None
    total: int | None = None
