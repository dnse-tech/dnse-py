"""Market data response models for DNSE SDK."""

from __future__ import annotations

from dnse.models.base import DnseBaseModel


class SecurityDefinition(DnseBaseModel):
    """Security definition from GET /price/secdef/{symbol}."""

    symbol: str | None = None
    market_id: str | None = None
    board_id: str | None = None
    isin: str | None = None
    product_grp_id: str | None = None
    security_group_id: str | None = None
    security_status: str | None = None
    symbol_admin_status_code: str | None = None
    symbol_trading_method_status_code: str | None = None
    symbol_trading_sanction_status_code: str | None = None
    basic_price: int | None = None
    ceiling_price: int | None = None
    floor_price: int | None = None
    open_interest_quantity: int | None = None
