import asyncio
import contextlib
from typing import TYPE_CHECKING, Any

from hllrcon.connection import RconConnection

if TYPE_CHECKING:
    from hllrcon.pooled.rcon import PooledRcon


class PooledRconWorker:
    def __init__(self, host: str, port: int, password: str, pool: "PooledRcon") -> None:
        self.host = host
        self.port = port
        self.password = password
        self.pool = pool

        self._connection: asyncio.Future[RconConnection] | None = None
        self._busy = False
        self._disconnected = False

    async def _get_connection(self) -> RconConnection:
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

    def is_busy(self) -> bool:
        return self._busy

    def is_disconnected(self) -> bool:
        return self._disconnected

    def on_disconnect(self) -> None:
        self._busy = False
        self._disconnected = True
        with contextlib.suppress(ValueError):
            self.pool.workers.remove(self)

    async def execute(
        self,
        command: str,
        version: int,
        body: str | dict[str, Any] = "",
    ) -> str:
        self._busy = True
        try:
            connection = await self._get_connection()
            return await connection.execute(command, version, body)
        finally:
            self._busy = False
