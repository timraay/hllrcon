import asyncio
import logging
import threading
from collections.abc import Generator
from concurrent.futures import Future
from contextlib import contextmanager
from typing import Any

from typing_extensions import override

from hllrcon.rcon import Rcon
from hllrcon.sync.commands import SyncRconCommands


class SyncRcon(SyncRconCommands):
    """A synchronous interface for connecting to an RCON server.

    This is a wrapper for the asynchronous `Rcon` class, which is being run in a
    separate thread with its own event loop.

    To execute commands concurrently, a new `execute_concurrently` method is provided,
    which returns a `concurrent.futures.Future` object.
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
        self._logger = logger
        self._rcon = Rcon(
            host,
            port,
            password,
            logger=logger,
            reconnect_after_failures=reconnect_after_failures,
        )
        self._loop: asyncio.AbstractEventLoop | None = None

    @property
    def host(self) -> str:
        return self._rcon.host

    @host.setter
    def host(self, value: str) -> None:
        self._rcon.host = value

    @property
    def port(self) -> int:
        return self._rcon.port

    @port.setter
    def port(self, value: int) -> None:
        self._rcon.port = value

    @property
    def password(self) -> str:
        return self._rcon.password

    @password.setter
    def password(self, value: str) -> None:
        self._rcon.password = value

    @property
    def logger(self) -> logging.Logger:
        return self._logger or logging.getLogger(__name__)

    @logger.setter
    def logger(self, value: logging.Logger | None) -> None:
        self._logger = value
        self._rcon.logger = value

    @property
    def reconnect_after_failures(self) -> int:
        return self._rcon.reconnect_after_failures

    @reconnect_after_failures.setter
    def reconnect_after_failures(self, value: int) -> None:
        self._rcon.reconnect_after_failures = value

    def is_connected(self) -> bool:
        """Check if the client is connected to the RCON server.

        Returns
        -------
        bool
            True if connected, False otherwise.

        """
        return (
            self._loop is not None
            and self._loop.is_running()
            and self._rcon.is_connected()
        )

    @contextmanager
    def connect(self) -> Generator[None]:
        """Establish a connection to the RCON server."""
        self.wait_until_connected()
        try:
            yield
        finally:
            self.disconnect()

    def wait_until_connected(self) -> None:
        """Wait until the client is connected to the RCON server.

        This might be useful to verify that a connection can be established before
        continuing with other operations.
        """
        if self._loop is None or not self._loop.is_running():
            event = threading.Event()

            def target() -> None:
                self._loop = asyncio.new_event_loop()
                self._loop.call_soon(event.set)
                self._loop.run_forever()

            threading.Thread(
                target=target,
                name=f"SyncRconThread{id(self)}",
                daemon=True,
            ).start()

            # Wait for the loop to have started
            if not event.wait(timeout=1):
                if self._loop is not None:
                    self._loop.stop()
                    self._loop = None
                msg = "Thread never signalled back"
                raise RuntimeError(msg) from None

        if self._loop is None:  # pragma: no cover
            msg = "Could not run event loop"
            raise RuntimeError(msg)

        asyncio.run_coroutine_threadsafe(
            self._rcon.wait_until_connected(),
            loop=self._loop,
        ).result()

    def disconnect(self) -> None:
        """Disconnect from the RCON server."""
        self._rcon.disconnect()
        if self._loop is not None:
            self._loop.stop()
        self._loop = None

    def execute_concurrently(
        self,
        command: str,
        version: int,
        body: str | dict[str, Any] = "",
    ) -> Future[str]:
        """Schedule the execution of a command on the RCON server.

        This method allows for concurrent execution of commands.

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
        concurrent.futures.Future[str]
            A Future representing the response from the server.

        """
        self.wait_until_connected()

        if self._loop is None:  # pragma: no cover
            msg = "Could not run event loop"
            raise RuntimeError(msg)

        return asyncio.run_coroutine_threadsafe(
            self._rcon.execute(command, version, body),
            loop=self._loop,
        )

    @override
    def execute(
        self,
        command: str,
        version: int,
        body: str | dict[str, Any] = "",
    ) -> str:
        return self.execute_concurrently(
            command=command,
            version=version,
            body=body,
        ).result()
