"""Custom exceptions for the Pecron API client."""


class PecronAPIError(Exception):
    """Base exception for Pecron API errors."""

    def __init__(self, message: str, code: int | None = None):
        self.code = code
        self.message = message
        super().__init__(f"API error {code}: {message}" if code else message)


class AuthenticationError(PecronAPIError):
    """Raised when login fails."""


class DeviceNotFoundError(PecronAPIError):
    """Raised when a device lookup fails (invalid pk/dk)."""


class CommandError(PecronAPIError):
    """Raised when a device command fails."""
