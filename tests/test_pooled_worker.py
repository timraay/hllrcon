import asyncio
from typing import Any
from unittest import mock

import pytest
from hllrcon.connection import RconConnection
from hllrcon.exceptions import HLLError
from hllrcon.pooled.rcon import PooledRcon
from hllrcon.pooled.worker import PooledRconWorker


@pytest.fixture
def pool() -> PooledRcon:
    pool = mock.Mock(spec=PooledRcon)
    pool._workers = mock.Mock(list)
    return pool


@pytest.fixture
def connection() -> RconConnection:
    mock_connection = mock.Mock(spec=RconConnection)
    mock_connection.is_connected.return_value = True
    return mock_connection


@pytest.fixture
def worker(
    monkeypatch: pytest.MonkeyPatch,
    pool: PooledRcon,
    connection: RconConnection,
) -> PooledRconWorker:
    """Fixture to create a mock PooledWorker."""

    async def get_connection(*_args: Any, **_kwargs: dict[str, Any]) -> RconConnection:  # noqa: ANN401
        return connection

    monkeypatch.setattr(RconConnection, "connect", get_connection)

    return PooledRconWorker(
        host="localhost",
        port=1234,
        password="password",
        pool=pool,
    )


@pytest.mark.asyncio
async def test_get_connection_new(
    worker: PooledRconWorker,
    connection: RconConnection,
) -> None:
    assert await worker._get_connection() == connection


@pytest.mark.asyncio
async def test_get_connection_failure(
    monkeypatch: pytest.MonkeyPatch,
    worker: PooledRconWorker,
) -> None:
    async def get_connection(*_args: Any, **_kwargs: dict[str, Any]) -> RconConnection:  # noqa: ANN401
        msg = "Connection failed"
        raise HLLError(msg)

    monkeypatch.setattr("hllrcon.rcon.RconConnection.connect", get_connection)

    with pytest.raises(HLLError, match="Connection failed"):
        await worker._get_connection()


@pytest.mark.asyncio
async def test_get_connection_reuse(
    worker: PooledRconWorker,
    connection: RconConnection,
) -> None:
    worker._connection = asyncio.Future()
    worker._connection.set_result(connection)
    assert await worker._get_connection() == connection


@pytest.mark.asyncio
async def test_get_connection_reuse_failure(
    worker: PooledRconWorker,
) -> None:
    worker._connection = asyncio.Future()
    worker._connection.set_exception(HLLError("Connection failed"))

    with pytest.raises(HLLError, match="Connection failed"):
        await worker._get_connection()


@pytest.mark.asyncio
async def test_get_connection_wait(
    worker: PooledRconWorker,
    connection: mock.Mock,
) -> None:
    worker._connection = asyncio.Future()

    with pytest.raises(asyncio.TimeoutError):
        async with asyncio.timeout(0.1):
            await worker._get_connection()

    asyncio.get_event_loop().call_soon(worker._connection.set_result, connection)
    async with asyncio.timeout(0.1):
        assert await worker._get_connection() == connection


def test_is_busy(worker: PooledRconWorker) -> None:
    assert not worker.is_busy()
    worker._busy = True
    assert worker.is_busy()
    worker._busy = False
    assert not worker.is_busy()


@pytest.mark.asyncio
async def test_is_connected(worker: PooledRconWorker, connection: mock.Mock) -> None:
    assert worker.is_connected() is False, "Should be disconnected initially"

    await worker._get_connection()
    assert worker.is_connected() is True, "Should be connected after getting connection"

    connection.is_connected.return_value = False
    assert worker.is_connected() is False, (
        "Should be disconnected after connection loss"
    )

    worker._connection = asyncio.Future()
    worker._connection.set_exception(HLLError("Connection lost"))
    assert worker.is_connected() is False, "Should be disconnected after exception"

    worker._connection = asyncio.Future()
    worker._connection.cancel()
    assert worker.is_connected() is False, "Should be disconnected after cancelling"


def test_is_disconnected(worker: PooledRconWorker) -> None:
    assert worker.is_disconnected() is False
    worker._disconnected = True
    assert worker.is_disconnected() is True
    worker._disconnected = False
    assert worker.is_disconnected() is False


@pytest.mark.asyncio
async def test_on_disconnected(
    worker: PooledRconWorker,
    connection: RconConnection,
) -> None:
    await worker._get_connection()

    assert worker.is_disconnected() is False
    worker._busy = True

    connection.on_disconnect()
    assert worker.is_disconnected() is True
    assert worker.is_busy() is False


@pytest.mark.asyncio
async def test_disconnect_while_connected(
    worker: PooledRconWorker,
    connection: mock.Mock,
) -> None:
    await worker._get_connection()

    assert not worker.is_disconnected()
    assert not worker.is_busy()

    worker.disconnect()

    assert worker.is_disconnected()
    assert not worker.is_busy()

    # Ensure the connection's disconnect method was called
    connection.disconnect.assert_called_once()


@pytest.mark.asyncio
async def test_disconnect_before_connecting(
    worker: PooledRconWorker,
) -> None:
    assert not worker.is_disconnected()
    assert not worker.is_busy()

    worker.disconnect()

    assert worker.is_disconnected()
    assert not worker.is_busy()


@pytest.mark.asyncio
async def test_disconnect_while_connecting(
    worker: PooledRconWorker,
) -> None:
    fut: asyncio.Future[RconConnection] = asyncio.Future()
    worker._connection = fut

    assert not worker.is_disconnected()
    assert not worker.is_busy()

    worker.disconnect()

    assert worker.is_disconnected()
    assert not worker.is_busy()

    # Ensure that the connection attempt was cancelled
    assert fut.cancelled() is True


@pytest.mark.asyncio
async def test_disconnect_while_exception(
    worker: PooledRconWorker,
) -> None:
    fut: asyncio.Future[RconConnection] = asyncio.Future()
    fut.set_exception(HLLError("Connection failed"))
    worker._connection = fut

    assert not worker.is_disconnected()
    assert not worker.is_busy()

    worker.disconnect()

    assert worker.is_disconnected()
    assert not worker.is_busy()


@pytest.mark.asyncio
async def test_disconnect_while_cancelled(
    worker: PooledRconWorker,
) -> None:
    fut: asyncio.Future[RconConnection] = asyncio.Future()
    fut.cancel()
    worker._connection = fut

    assert not worker.is_disconnected()
    assert not worker.is_busy()

    worker.disconnect()

    assert worker.is_disconnected()
    assert not worker.is_busy()


@pytest.mark.asyncio
async def test_execute(
    worker: PooledRconWorker,
    connection: mock.Mock,
) -> None:
    command = "test_command"
    version = 1
    body = "test_body"

    # Mock the execute method of the connection
    connection.execute = mock.AsyncMock(return_value="response")

    response = await worker.execute(command, version, body)

    assert response == "response"
    connection.execute.assert_awaited_once_with(command, version, body)
