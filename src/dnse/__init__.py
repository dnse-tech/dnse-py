"""DNSE Python SDK."""

try:
    from dnse._version import __version__
except ModuleNotFoundError:
    __version__ = "0.0.0+dev"

from dnse.async_client import AsyncDnseClient
from dnse.client import DnseClient
from dnse.exceptions import (
    DnseAPIError,
    DnseAuthError,
    DnseError,
    DnseRateLimitError,
    DnseSessionExpiredError,
)
from dnse.models import (
    AccountBalanceResponse,
    AccountsResponse,
    AccountSubItem,
    BoardId,
    DealItem,
    DealsResponse,
    DnseBaseModel,
    GetOrdersResponse,
    LoanPackage,
    LoanPackageResponse,
    OrderHistoryResponse,
    OrderItem,
    PlaceOrderRequest,
    PlaceOrderResponse,
    PpseResponse,
    SecurityDefinition,
    StockBalance,
    TwoFARequest,
    TwoFAResponse,
    UpdateOrderRequest,
)
from dnse.stream import DnseMarketStream, DnseTradingStream
from dnse.stream.exceptions import DnseStreamError

__all__ = [
    "__version__",
    # clients
    "DnseClient",
    "AsyncDnseClient",
    # exceptions
    "DnseError",
    "DnseAPIError",
    "DnseAuthError",
    "DnseRateLimitError",
    "DnseSessionExpiredError",
    # stream
    "DnseMarketStream",
    "DnseTradingStream",
    "DnseStreamError",
    # base model
    "DnseBaseModel",
    # auth models
    "TwoFARequest",
    "TwoFAResponse",
    # account models
    "AccountSubItem",
    "AccountsResponse",
    "StockBalance",
    "AccountBalanceResponse",
    "LoanPackage",
    "LoanPackageResponse",
    "PpseResponse",
    # deal models
    "DealItem",
    "DealsResponse",
    # market models
    "BoardId",
    "SecurityDefinition",
    # order models
    "PlaceOrderRequest",
    "PlaceOrderResponse",
    "OrderItem",
    "GetOrdersResponse",
    "UpdateOrderRequest",
    "OrderHistoryResponse",
]
