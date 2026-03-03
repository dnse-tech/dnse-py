"""Market data response models for DNSE SDK."""

from __future__ import annotations

from enum import Enum

from pydantic import field_validator

from dnse.models.base import DnseBaseModel


class BoardId(str, Enum):
    """Board ID for filtering security definitions.

    Values are the short codes the server accepts (BOARD_ID_<VALUE> without the prefix).
    Use the descriptive member names in your code for readability.
    """

    ALL = "AL"  # All boards
    ROUND_LOT = "G1"  # Round lot (regular session)
    AFTER_HOURS_PLO = "G3"  # After-hours PLO session
    ODD_LOT = "G4"  # Odd lot
    PT_ROUND_LOT_MORNING = "T1"  # Put-through round lot 9h-14h45
    PT_ROUND_LOT_AFTERNOON = "T3"  # Put-through round lot 14h45-15h
    PT_ODD_LOT_MORNING = "T4"  # Put-through odd lot 9h-14h45
    PT_ODD_LOT_AFTERNOON = "T6"  # Put-through odd lot 14h45-15h


class SecurityDefinition(DnseBaseModel):
    """Security definition from GET /price/secdef/{symbol}."""

    symbol: str | None = None
    market_id: str | None = None
    board_id: BoardId | str | None = (
        None  # BoardId for known codes; falls back to raw str for unknown
    )
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

    @field_validator("board_id", mode="before")
    @classmethod
    def coerce_board_id(cls, v: object) -> object:
        """Coerce string board_id to BoardId enum when the code is known."""
        if isinstance(v, str):
            try:
                return BoardId(v)
            except ValueError:
                return v
        return v
