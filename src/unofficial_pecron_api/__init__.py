"""Unofficial Python API client for Pecron portable power stations."""

__version__ = "0.1.0"

from .client import PecronAPI
from .const import Region
from .exceptions import AuthenticationError, DeviceNotFoundError, PecronAPIError
from .models import Device, DeviceProperties

__all__ = [
    "PecronAPI",
    "Region",
    "Device",
    "DeviceProperties",
    "PecronAPIError",
    "AuthenticationError",
    "DeviceNotFoundError",
]
