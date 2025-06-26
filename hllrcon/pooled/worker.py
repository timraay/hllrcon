import asyncio
import contextlib
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any

from hllrcon.connection import RconConnection

if TYPE_CHECKING:
    from hllrcon.pooled.rcon import PooledRcon


class PooledRconWorker:
    """A worker for executing RCON commands in a pooled RCON client."""

    def __init__(self, host: str, port: int, password: str, pool: "PooledRcon") -> None:
        """Initializes a new pooled RCON worker.

        Parameters
        ----------
        host : str
            The hostname or IP address of the RCON server.
        port : int
            The port number of the RCON server.
        password : str
            The password for the RCON connection.
        pool : PooledRcon
            The pooled RCON client that manages this worker.

        """
        self.host = host
        self.port = port
        self.password = password
        self.pool = pool

        self._connection: asyncio.Future[RconConnection] | None = None
        self._busy = False
        self._disconnected = False

    async def _get_connection(self) -> RconConnection:
        """Get the RCON connection for this worker.

        A new connection will be established the first time this method is called.

        The worker will not make any attempts to reconnect if the connection is lost.
        Instead, a new worker should be created to handle future requests.

        Raises
        ------
        HLLConnectionError
            The address and port could not be resolved.
        HLLConnectionRefusedError
            The server refused the connection.
        HLLAuthError
            The provided password is incorrect.

        Returns
        -------
        RconConnection
            The RCON connection for this worker.

        """
        if self._connection:
            return await asyncio.shield(self._connection)

        self._connection = asyncio.Future()
        try:
            connection = await RconConnection.connect(
                host=self.host,
                port=self.port,
                password=self.password,
            )
            connection.on_disconnect = self.on_disconnect
            self._connection.set_result(connection)
        except Exception as e:
            self._connection.set_exception(e)
            self.on_disconnect()
            raise
        else:
            return connection

    def disconnect(self) -> None:
        if self._connection:
            if self._connection.done():
                if (
                    not self._connection.cancelled()
                    and not self._connection.exception()
                ):
                    self._connection.result().disconnect()
            else:
                self._connection.cancel()

        self.on_disconnect()

    def is_busy(self) -> bool:
        """Check if the worker is currently busy executing a command.

        Returns
        -------
        bool
            True if the worker is busy, False otherwise.

        """
        return self._busy

    def is_connected(self) -> bool:
        """Check if the worker is connected to the RCON server.

        Returns
        -------
        bool
            True if the worker is connected, False otherwise.

        """
        return (
            self._connection is not None
            and not self._connection.cancelled()
            and self._connection.done()
            and not self._connection.exception()
            and self._connection.result().is_connected()
        )

    def is_disconnected(self) -> bool:
        """Check if the worker is disconnected from the RCON server.

        Returns
        -------
        bool
            True if the worker is disconnected, False otherwise.

        """
        return self._disconnected

    def on_disconnect(self) -> None:
        """Clean up the worker when the connection is lost."""
        self._busy = False
        self._disconnected = True
        with contextlib.suppress(ValueError):
            self.pool._workers.remove(self)  # noqa: SLF001

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncGenerator[RconConnection, None]:
        self._busy = True
        try:
            connection = await self._get_connection()
            yield connection
        finally:
            self._busy = False

    async def execute(
        self,
        command: str,
        version: int,
        body: str | dict[str, Any] = "",
    ) -> str:
        """Execute a command on the RCON server.

        Parameters
        ----------
        command : str
            The command to execute.
        version : int
            The version of the command to execute.
        body : str | dict[str, Any], optional
            The body of the command, by default an empty string.

        Returns
        -------
        str
            The response from the server.

        """
        async with self.connect() as connection:
            return await connection.execute(command, version, body)
