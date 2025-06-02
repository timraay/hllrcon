import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from typing_extensions import override

from hllrcon.commands import RconCommands
from hllrcon.pooled.worker import PooledRconWorker


class PooledRcon(RconCommands):
    def __init__(
        self,
        host: str,
        port: int,
        password: str,
        pool_size: int,
    ) -> None:
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
        worker: PooledRconWorker | None = None

        while worker is None or worker.is_disconnected():
            if self._queue.empty() and len(self.workers) < self.pool_size:
                worker = PooledRconWorker(
                    host=self.host,
                    port=self.port,
                    password=self.password,
                    pool=self,
                )
                self.workers.append(worker)

            else:
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
