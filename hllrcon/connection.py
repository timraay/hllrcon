import asyncio
from typing import TYPE_CHECKING, Any

from hllrcon.commands import RconCommands
from hllrcon.exceptions import HLLConnectionLostError
from hllrcon.protocol.protocol import RconProtocol

if TYPE_CHECKING:
    from collections.abc import Callable


class RconConnection(RconCommands):
    """A class representing a connection to an RCON server.

    RconConnections are single-use and cannot be reused after being disconnected from
    the RCON server. For a RCON client that includes recovery mechanisms for connection
    issues, refer to ~`Rcon` instead.
    """

    def __init__(self, protocol: RconProtocol) -> None:
        self._protocol = protocol
        self._disconnect_event: asyncio.Event = asyncio.Event()
        self._disconnect_event.set()

        self.on_disconnect: Callable[[], None] = lambda: None

    def is_connected(self) -> bool:
        """Check if the connection is still active."""
        return self._protocol.is_connected()

    def disconnect(self) -> None:
        """Disconnect from the RCON server."""
        self._protocol.disconnect()

    def _on_disconnect(self, _: Exception | None) -> None:
        """Internal callback for when the connection is lost."""
        self._disconnect_event.set()
        self.on_disconnect()

    async def wait_until_disconnected(self) -> None:
        """Wait until the connection is closed."""
        await self._disconnect_event.wait()

    @classmethod
    async def connect(
        cls,
        host: str,
        port: int,
        password: str,
    ) -> "RconConnection":
        """Connect to the RCON server."""
        protocol = await RconProtocol.connect(
            host=host,
            port=port,
            password=password,
        )
        self = cls(protocol)

        self._disconnect_event.clear()
        self._protocol.on_connection_lost = self._on_disconnect

        return self

    async def execute(
        self,
        command: str,
        version: int,
        body: str | dict[str, Any] = "",
    ) -> str:
        if self._disconnect_event.is_set():
            raise HLLConnectionLostError
        response = await self._protocol.execute(command, version, body)
        return response.content_body
