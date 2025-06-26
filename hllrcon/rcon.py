import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from typing_extensions import override

from hllrcon.client import RconClient
from hllrcon.connection import RconConnection


class Rcon(RconClient):
    """An inferface for connecting to an RCON server.

    This class will (re)connect to the RCON server on-demand. Only when no connection is
    available at the time of executing a command will a new connection be attempted to
    be established.
    """

    def __init__(self, host: str, port: int, password: str) -> None:
        """Initialize a new `Rcon` instance.

        Parameters
        ----------
        host : str
            The hostname or IP address of the RCON server.
        port : int
            The port of the RCON server.
        password : str
            The password for the RCON server.

        """
        super().__init__()
        self.host = host
        self.port = port
        self.password = password

        self._connection: asyncio.Future[RconConnection] | None = None

    async def _get_connection(self) -> RconConnection:
        if (
            self._connection
            and self._connection.done()
            and (
                self._connection.exception()
                or not self._connection.result().is_connected()
            )
        ):
            self._connection = None

        if self._connection is None:
            self._connection = asyncio.Future()
            try:
                connection = await RconConnection.connect(
                    host=self.host,
                    port=self.port,
                    password=self.password,
                )
                self._connection.set_result(connection)
            except Exception as e:
                self._connection.set_exception(e)
                self._connection = None
                raise
            else:
                return connection

        elif not self._connection.done():
            return await asyncio.shield(self._connection)

        else:
            return self._connection.result()

    @override
    def is_connected(self) -> bool:
        return (
            self._connection is not None
            and not self._connection.cancelled()
            and self._connection.done()
            and not self._connection.exception()
            and self._connection.result().is_connected()
        )

    @override
    @asynccontextmanager
    async def connect(self) -> AsyncGenerator[None]:
        await self._get_connection()
        try:
            yield
        finally:
            self.disconnect()

    @override
    def disconnect(self) -> None:
        if self._connection:
            if self._connection.done():
                if not self._connection.exception():
                    self._connection.result().disconnect()
            else:
                self._connection.cancel()

        self._connection = None

    @override
    async def execute(
        self,
        command: str,
        version: int,
        body: str | dict[str, Any] = "",
    ) -> str:
        connection = await self._get_connection()
        return await connection.execute(command, version, body)
