import asyncio
import threading
from collections.abc import Generator
from concurrent.futures import Future
from contextlib import contextmanager
from typing import Any

from hllrcon.rcon import Rcon
from hllrcon.sync.commands import SyncRconCommands


class SyncRcon(SyncRconCommands):
    """A synchronous interface for connecting to an RCON server.

    This is a wrapper for the asynchronous `Rcon` class, which is being run in a
    separate thread with its own event loop.

    To execute commands concurrently, a new `execute_concurrently` method is provided,
    which returns a `concurrent.futures.Future` object.
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
        self._rcon = Rcon(host, port, password)
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

    def execute(
        self,
        command: str,
        version: int,
        body: str | dict[str, Any] = "",
    ) -> str:
        self.wait_until_connected()

        if self._loop is None:  # pragma: no cover
            msg = "Could not run event loop"
            raise RuntimeError(msg)

        return asyncio.run_coroutine_threadsafe(
            self._rcon.execute(command, version, body),
            loop=self._loop,
        ).result()

    def execute_concurrently(
        self,
        command: str,
        version: int,
        body: str | dict[str, Any] = "",
    ) -> Future[str]:
        self.wait_until_connected()

        if self._loop is None:  # pragma: no cover
            msg = "Could not run event loop"
            raise RuntimeError(msg)

        return asyncio.run_coroutine_threadsafe(
            self._rcon.execute(command, version, body),
            loop=self._loop,
        )
