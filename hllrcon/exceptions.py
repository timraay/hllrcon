class HLLError(Exception):
    """Base exception for all HLL-related errors."""


class HLLCommandError(HLLError):
    """Raised when the game server returns an error for a request."""

    def __init__(self, status_code: int, *args: object) -> None:
        self.status_code = status_code
        super().__init__(*args)


class HLLMessageError(HLLError):
    """Raised when the game server returns an unexpected value."""


class HLLConnectionError(HLLError):
    """Generic error for connection errors."""


class HLLConnectionRefusedError(HLLConnectionError):
    """Raised when the connection is refused."""


class HLLAuthError(HLLConnectionError):
    """Raised for failed authentication."""


class HLLConnectionLostError(HLLConnectionError):
    """Raised when the connection to the server is lost."""
