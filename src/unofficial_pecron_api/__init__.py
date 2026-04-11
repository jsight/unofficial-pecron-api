"""Unofficial Python API client for Pecron portable power stations."""

__version__ = "0.4.0"

from .client import PecronAPI
from .const import Region
from .exceptions import AuthenticationError, CommandError, DeviceNotFoundError, PecronAPIError
from .models import (
    CommandResult,
    Device,
    DeviceProperties,
    TslEnumValue,
    TslIntSpec,
    TslProperty,
)

__all__ = [
    "PecronAPI",
    "Region",
    "CommandResult",
    "Device",
    "DeviceProperties",
    "TslEnumValue",
    "TslIntSpec",
    "TslProperty",
    "PecronAPIError",
    "AuthenticationError",
    "CommandError",
    "DeviceNotFoundError",
]
