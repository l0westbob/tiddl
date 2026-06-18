"""Compatibility package surface for tidal provider usage.

The concrete implementations are kept in `tiddl.providers.tidal` while core
facade exports remain available for existing imports.
"""

from .api import TidalAPI
from .auth import AuthAPI
from .client import TidalClient
from .exceptions import ApiError, AuthClientError
from tiddl.core.api.api import Limits

__all__ = [
    "ApiError",
    "AuthAPI",
    "AuthClientError",
    "Limits",
    "TidalAPI",
    "TidalClient",
]
