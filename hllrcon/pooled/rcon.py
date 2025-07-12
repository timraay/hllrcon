import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from typing_extensions import override

from hllrcon.client import RconClient
from hllrcon.pooled.worker import PooledRconWorker


class PooledRcon(RconClient):
    """A pooled RCON client that that manages multiple connections to an RCON server.

    This class allows for concurrent execution of commands by maintaining a pool of
    RCON workers. Each worker can handle a command execution independently, which
    improves performance and reduces latency for multiple requests.

    This class will eventually be deprecated once the RCON protocol supports concurrent
    requests.

    """

    def __init__(
        self,
        host: str,
        port: int,
        password: str,
        max_workers: int,
    ) -> None:
        """Initializes a new pooled RCON client.

        Parameters
        ----------
        host : str
            The hostname or IP address of the RCON server.
        port : int
            The port number of the RCON server.
        password : str
            The password for the RCON connection.
        max_workers : int
            The maximum number of concurrent workers in the pool.

        """
        if max_workers <= 0:
            msg = "Max workers must be greater than 0"
            raise ValueError(msg)

        self.host = host
        self.port = port
        self.password = password
        self.max_workers = max_workers

        self._workers: list[PooledRconWorker] = []
        self._queue: asyncio.Queue[PooledRconWorker] = asyncio.Queue()

    @property
    def num_workers(self) -> int:
        """Get the number of workers currently in the pool.

        Returns
        -------
        int
            The number of workers currently in the pool.

        """
        return len(self._workers)

    @asynccontextmanager
    async def _get_available_worker(self) -> AsyncGenerator[PooledRconWorker]:
        """Wait for a worker to become available.

        If all workers are busy and the pool is not full, a new worker is created
        instead.

        Yields
        ------
        PooledRconWorker
            An available worker from the pool.

        """
        worker: PooledRconWorker | None = None

        while worker is None or worker.is_disconnected():
            if self._queue.empty() and len(self._workers) < self.max_workers:
                # No workers are available and we have not yet reached the max amount of
                # workers. Yield a new worker and add it to the pool.
                worker = PooledRconWorker(
                    host=self.host,
                    port=self.port,
                    password=self.password,
                    pool=self,
                )
                self._workers.append(worker)

            else:
                # Wait for an available worker from the queue.
                worker = await self._queue.get()

        try:
            yield worker
        finally:
            self._queue.put_nowait(worker)

    @override
    def is_connected(self) -> bool:
        """Check if any worker in the pool is connected to the RCON server.

        Returns
        -------
        bool
            True if at least one worker is connected, False otherwise.

        """
        return any(worker.is_connected() for worker in self._workers)

    @override
    @asynccontextmanager
    async def connect(self) -> AsyncGenerator[None]:
        """Establish a connection to the RCON server.

        Because this is a pooled client, connections are not established immediately.
        Once leaving this context, all workers will be disconnected again.
        """
        try:
            yield
        finally:
            # Disconnect all workers when done.
            self.disconnect()

    @override
    async def wait_until_connected(self) -> None:
        available_workers = [
            worker for worker in self._workers if not worker.is_disconnected()
        ]

        # If no workers are available, create a new one.
        if not available_workers:
            async with self._get_available_worker() as worker:
                await worker.wait_until_connected()

        else:
            # Check if any worker is connected.
            for worker in available_workers:
                if worker.is_connected():
                    return

            # Otherwise, wait for one to connect.
            await asyncio.wait(
                [
                    asyncio.ensure_future(worker.wait_until_connected())
                    for worker in available_workers
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

    @override
    def disconnect(self) -> None:
        """Disconnect from the RCON server.

        This method disconnects all workers in the pool.
        """
        for worker in self._workers:
            worker.disconnect()

        self._workers.clear()
        while not self._queue.empty():
            self._queue.get_nowait()

    @override
    async def execute(
        self,
        command: str,
        version: int,
        body: str | dict[str, Any] = "",
    ) -> str:
        async with self._get_available_worker() as worker:
            return await worker.execute(command, version, body)
