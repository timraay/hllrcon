class HLLError(Exception):
    """Base exception for all HLL-related errors."""


class HLLCommandError(HLLError):
    """Raised when the game server returns an error for a request."""

    def __init__(self, status_code: int, *args: object) -> None:
        """Initialize a new `HLLCommandError` instance.

        Parameters
        ----------
        status_code : int
            The status code returned by the server.
        *args : object
            Additional arguments to pass to the base exception.

        """
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
