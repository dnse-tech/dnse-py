"""DNSE Python SDK."""

try:
    from dnse._version import __version__
except ModuleNotFoundError:
    __version__ = "0.0.0+dev"

from dnse.exceptions import DnseAPIError, DnseAuthError, DnseError, DnseRateLimitError
from dnse.client import DnseClient
from dnse.async_client import AsyncDnseClient

__all__ = [
    "__version__",
    "DnseError",
    "DnseAPIError",
    "DnseAuthError",
    "DnseRateLimitError",
    "DnseClient",
    "AsyncDnseClient",
]
