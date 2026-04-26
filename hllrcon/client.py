from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TypeAlias

from hllrcon.commands import HLLRconCommands, HLLVRconCommands, _RconCommands

__all__ = (
    "HLLRconClient",
    "HLLVRconClient",
    "RconClient",
)


class _RconClient(_RconCommands, ABC):
    """Abstract base class for RCON clients.

    This class defines the interface for RCON clients, including methods for
    connecting, disconnecting, sending commands.
    """

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the client is connected to the RCON server.

        Returns
        -------
        bool
            True if connected, False otherwise.

        """

    @abstractmethod
    @asynccontextmanager
    async def connect(self) -> AsyncGenerator[None]:
        """Establish a connection to the RCON server."""
        yield

    @abstractmethod
    async def wait_until_connected(self) -> None:
        """Wait until the client is connected to the RCON server.

        This might be useful to verify that a connection can be established before
        continuing with other operations.
        """

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the RCON server."""


class HLLRconClient(HLLRconCommands, _RconClient):
    pass


class HLLVRconClient(HLLVRconCommands, _RconClient):
    pass


RconClient: TypeAlias = HLLRconClient | HLLVRconClient
