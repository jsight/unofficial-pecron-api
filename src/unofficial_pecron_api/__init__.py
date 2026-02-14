"""Unofficial Python API client for Pecron portable power stations."""

__version__ = "0.2.0"

from .client import PecronAPI
from .const import Region
from .exceptions import AuthenticationError, CommandError, DeviceNotFoundError, PecronAPIError
from .models import CommandResult, Device, DeviceProperties, TslProperty

__all__ = [
    "PecronAPI",
    "Region",
    "CommandResult",
    "Device",
    "DeviceProperties",
    "TslProperty",
    "PecronAPIError",
    "AuthenticationError",
    "CommandError",
    "DeviceNotFoundError",
]
