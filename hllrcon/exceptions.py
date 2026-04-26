__all__ = (
    "RconAuthError",
    "RconCommandError",
    "RconConnectionClosedError",
    "RconConnectionError",
    "RconConnectionLostError",
    "RconConnectionRefusedError",
    "RconError",
    "RconMessageError",
)


class RconError(Exception):
    """Base exception for all HLL-related errors."""


class RconCommandError(RconError):
    """Raised when the game server returns an error for a request."""

    def __init__(self, status_code: int, *args: object) -> None:
        """Initialize a new `RconCommandError` instance.

        Parameters
        ----------
        status_code : int
            The status code returned by the server.
        *args : object
            Additional arguments to pass to the base exception.

        """
        self.status_code = status_code
        super().__init__(*args)

    def __str__(self) -> str:
        """Return a string representation of the error."""
        exc_str = super().__str__()
        header = f"({self.status_code})"
        return f"{header} {exc_str}".rstrip()


class RconMessageError(RconError):
    """Raised when the game server returns an unexpected value."""


class RconConnectionError(RconError):
    """Generic error for connection errors."""


class RconConnectionRefusedError(RconConnectionError):
    """Raised when the connection is refused."""


class RconAuthError(RconConnectionError):
    """Raised for failed authentication."""


class RconConnectionClosedError(RconConnectionError):
    """Raised when the connection is closed."""


class RconConnectionLostError(RconConnectionClosedError):
    """Raised when the connection to the server is unexpectedly lost."""


class RconWarning(UserWarning):
    """Base warning for all warnings emitted by the hllrcon library."""
