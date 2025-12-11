import asyncio
import logging
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

    def __init__(
        self,
        host: str,
        port: int,
        password: str,
        logger: logging.Logger | None = None,
        reconnect_after_failures: int = 3,
    ) -> None:
        """Initialize a new `Rcon` instance.

        Parameters
        ----------
        host : str
            The hostname or IP address of the RCON server.
        port : int
            The port of the RCON server.
        password : str
            The password for the RCON server.
        logger : logging.Logger | None, optional
            A logger instance for logging messages, by default None. If None,
            `logging.getLogger(__name__)` is used.
        reconnect_after_failures : int, optional
            After how many failed attempts to execute a command the active connection is
            disposed and a new connection is established on the next command execution.
            If the server responds to a request, the failure count is reset, even if the
            server returned an error. Set to 0 to disable, by default 3.

        """
        super().__init__()
        self.host = host
        self.port = port
        self.password = password
        self.reconnect_after_failures = max(0, reconnect_after_failures)

        self._logger = logger
        self._connection: asyncio.Future[RconConnection] | None = None
        self._failure_count = 0

    @property
    def logger(self) -> logging.Logger:
        return self._logger or logging.getLogger(__name__)

    @logger.setter
    def logger(self, value: logging.Logger | None) -> None:
        self._logger = value

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
                    logger=self._logger,
                )
                self._connection.set_result(connection)
            except Exception as e:
                old_connection = self._connection
                self._connection = None

                # Set the result, in case anyone is awaiting it
                old_connection.set_exception(e)
                # We grab the result in case noone is awaiting it, to avoid "Future
                # exception was never retrieved" warnings
                old_connection.result()
                raise  # pragma: no cover
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
    async def wait_until_connected(self) -> None:
        await self._get_connection()

    @override
    def disconnect(self) -> None:
        if self._connection:
            if self._connection.done():
                if not self._connection.exception():
                    self._connection.result().disconnect()
            else:
                self._connection.cancel()

        self._connection = None
        self._failure_count = 0

    @override
    async def execute(
        self,
        command: str,
        version: int,
        body: str | dict[str, Any] = "",
    ) -> str:
        connection = await self._get_connection()

        try:
            return await connection.execute(command, version, body)
        except (TimeoutError, OSError):
            self._failure_count += 1
            if (
                self.reconnect_after_failures > 0
                and self._failure_count >= self.reconnect_after_failures
            ):
                self.disconnect()
            raise
