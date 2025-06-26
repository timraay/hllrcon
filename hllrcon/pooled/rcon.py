import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from typing_extensions import override

from hllrcon.commands import RconCommands
from hllrcon.pooled.worker import PooledRconWorker


class PooledRcon(RconCommands):
    """A pooled RCON client that that manages multiple connections to an RCON server.

    This class allows for concurrent execution of commands by maintaining a pool of
    RCON workers. Each worker can handle a command execution independently, which
    improves performance and reduces latency for multiple requests.


    """

    def __init__(
        self,
        host: str,
        port: int,
        password: str,
        pool_size: int,
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
        pool_size : int
            The maximum number of concurrent connections in the pool.

        """
        if pool_size <= 0:
            msg = "Pool size must be greater than 0"
            raise ValueError(msg)

        self.host = host
        self.port = port
        self.password = password
        self.pool_size = pool_size

        self.workers: list[PooledRconWorker] = []
        self._queue: asyncio.Queue[PooledRconWorker] = asyncio.Queue()

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
            if self._queue.empty() and len(self.workers) < self.pool_size:
                # No workers are available and we have not yet reached the pool size.
                # Yield a new worker and add it to the pool.
                worker = PooledRconWorker(
                    host=self.host,
                    port=self.port,
                    password=self.password,
                    pool=self,
                )
                self.workers.append(worker)

            else:
                # Wait for an available worker from the queue.
                worker = await self._queue.get()

        try:
            yield worker
        finally:
            self._queue.put_nowait(worker)

    @override
    async def execute(
        self,
        command: str,
        version: int,
        body: str | dict[str, Any] = "",
    ) -> str:
        async with self._get_available_worker() as worker:
            return await worker.execute(command, version, body)
