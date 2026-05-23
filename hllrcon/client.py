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
    async def connection(self) -> AsyncGenerator[None]:
        """Establish a connection to the RCON server and disconnect when done.

        This method is equivalent to the following code.

        .. code-block:: python

            await self.connect()
            try:
                yield
            finally:
                self.disconnect()
        """
        yield

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the RCON server.

        This method can be used to explicitly establish a connection and might be useful
        to verify that a connection can be established before continuing with other
        operations. However, it is not strictly necessary as the client will also
        connect on demand.
        """

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the RCON server."""


class HLLRconClient(HLLRconCommands, _RconClient):
    pass


class HLLVRconClient(HLLVRconCommands, _RconClient):
    pass


RconClient: TypeAlias = HLLRconClient | HLLVRconClient
