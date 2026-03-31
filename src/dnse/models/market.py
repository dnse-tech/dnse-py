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


class MarketId(int, Enum):
    """Market ID identifying the exchange/market segment."""

    UNSPECIFIED = 0  # Không xác định
    DVX = 3  # Phái sinh sàn HNX
    HCX = 4  # Trái phiếu doanh nghiệp sàn HNX
    STO = 6  # Cổ phiếu sàn HOSE
    STX = 7  # Cổ phiếu sàn HNX
    UPX = 8  # Cổ phiếu sàn Upcom


class ProductGrpId(int, Enum):
    """Product group ID classifying the instrument category."""

    UNSPECIFIED = 0  # Không xác định
    FBX = 3  # Hợp đồng tương lai Trái phiếu
    FIO = 4  # Hợp đồng tương lai Chỉ số
    HCX = 5  # Trái phiếu Doanh nghiệp HNX
    STO = 7  # Cổ phiếu sàn HOSE
    STX = 8  # Cổ phiếu sàn HNX
    UPX = 9  # Cổ phiếu sàn Upcom


class SecurityGroupId(int, Enum):
    """Security group ID classifying the instrument type."""

    UNSPECIFIED = 0  # Không xác định
    BS = 1  # Trái phiếu doanh nghiệp
    EF = 2  # Quỹ ETF
    EW = 3  # Chứng quyền
    FU = 4  # Hợp đồng tương lai
    SR = 6  # Quyền mua
    ST = 7  # Cổ phiếu


class SecurityStatus(int, Enum):
    """Security trading halt status."""

    HALT = 1  # Ngừng giao dịch
    NO_HALT = 2  # Không ngừng giao dịch


def _coerce_int_enum(enum_cls: type, v: object) -> object:
    """Try to coerce int or int-string to an int enum; return raw value on failure."""
    if v is None:
        return v
    try:
        return enum_cls(int(v))  # type: ignore[call-arg]
    except (ValueError, TypeError):
        return v


class SecurityDefinition(DnseBaseModel):
    """Security definition from GET /price/{symbol}/secdef."""

    symbol: str | None = None
    market_id: MarketId | int | str | None = (
        None  # MarketId for known int codes; falls back to raw int/str
    )
    board_id: BoardId | str | None = (
        None  # BoardId for known codes; falls back to raw str for unknown
    )
    isin: str | None = None
    product_grp_id: ProductGrpId | int | str | None = None  # ProductGrpId for known int codes
    security_group_id: SecurityGroupId | int | str | None = (
        None  # SecurityGroupId for known int codes
    )
    security_status: SecurityStatus | int | str | None = None  # SecurityStatus for known int codes
    symbol_admin_status_code: str | None = None
    symbol_trading_method_status_code: str | None = None
    symbol_trading_sanction_status_code: str | None = None
    basic_price: float | int | None = None
    ceiling_price: float | int | None = None
    floor_price: float | int | None = None
    open_interest_quantity: float | int | None = None

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

    @field_validator("market_id", mode="before")
    @classmethod
    def coerce_market_id(cls, v: object) -> object:
        """Coerce market_id to MarketId enum when the code is known."""
        return _coerce_int_enum(MarketId, v)

    @field_validator("product_grp_id", mode="before")
    @classmethod
    def coerce_product_grp_id(cls, v: object) -> object:
        """Coerce product_grp_id to ProductGrpId enum when the code is known."""
        return _coerce_int_enum(ProductGrpId, v)

    @field_validator("security_group_id", mode="before")
    @classmethod
    def coerce_security_group_id(cls, v: object) -> object:
        """Coerce security_group_id to SecurityGroupId enum when the code is known."""
        return _coerce_int_enum(SecurityGroupId, v)

    @field_validator("security_status", mode="before")
    @classmethod
    def coerce_security_status(cls, v: object) -> object:
        """Coerce security_status to SecurityStatus enum when the code is known."""
        return _coerce_int_enum(SecurityStatus, v)
