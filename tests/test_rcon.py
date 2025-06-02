import asyncio
import contextlib
from typing import Any
from unittest import mock

import pytest
from hllrcon.connection import RconConnection
from hllrcon.exceptions import HLLError
from hllrcon.rcon import Rcon

pytestmark = pytest.mark.asyncio


@pytest.fixture
def connection() -> RconConnection:
    mock_connection = mock.Mock(spec=RconConnection)
    mock_connection.is_connected.return_value = True
    return mock_connection


@pytest.fixture
def connection2() -> RconConnection:
    mock_connection = mock.Mock(spec=RconConnection)
    mock_connection.is_connected.return_value = True
    return mock_connection


@pytest.fixture
def rcon(monkeypatch: pytest.MonkeyPatch, connection: mock.Mock) -> Rcon:
    async def get_connection(*_args: Any, **_kwargs: dict[str, Any]) -> RconConnection:  # noqa: ANN401
        return connection

    monkeypatch.setattr("hllrcon.rcon.RconConnection.connect", get_connection)
    return Rcon(host="localhost", port=1234, password="password")


async def test_get_connection_new(rcon: Rcon, connection: mock.Mock) -> None:
    assert await rcon._get_connection() == connection


async def test_get_connection_reuse(
    rcon: Rcon,
    connection2: mock.Mock,
) -> None:
    rcon._connection = asyncio.Future()
    rcon._connection.set_result(connection2)
    assert await rcon._get_connection() == connection2


async def test_get_connection_disconnected(
    rcon: Rcon,
    connection: mock.Mock,
    connection2: mock.Mock,
) -> None:
    rcon._connection = asyncio.Future()
    rcon._connection.set_result(connection2)
    connection2.is_connected.return_value = False

    assert await rcon._get_connection() == connection


async def test_get_connection_wait(
    rcon: Rcon,
    connection2: mock.Mock,
) -> None:
    rcon._connection = asyncio.Future()

    with pytest.raises(asyncio.TimeoutError):
        async with asyncio.timeout(0.1):
            await rcon._get_connection()

    rcon._connection.set_result(connection2)
    assert await rcon._get_connection() == connection2


async def test_get_connection_failure(
    monkeypatch: pytest.MonkeyPatch,
    rcon: Rcon,
    connection: mock.Mock,
) -> None:
    with monkeypatch.context() as m:

        async def get_connection(
            *_args: Any,  # noqa: ANN401
            **_kwargs: dict[str, Any],
        ) -> RconConnection:
            msg = "Connection failed"
            raise HLLError(msg)

        m.setattr("hllrcon.rcon.RconConnection.connect", get_connection)

        with pytest.raises(HLLError, match="Connection failed"):
            await rcon._get_connection()

    assert await rcon._get_connection() == connection


async def test_enter_exit(rcon: Rcon, connection: mock.Mock) -> None:
    assert rcon._connection is None, "Initial connection should be None"

    async with rcon as conn:
        assert rcon._connection is not None, "Connection should be established"
        assert rcon._connection.result() == conn

    connection.disconnect.assert_called_once()
    assert rcon._connection is None, "Connection should be reset to None after exit"

    connection.disconnect.reset_mock()

    with contextlib.suppress(RuntimeError):
        async with rcon as conn:
            assert rcon._connection is not None, (
                "Connection should be established again"
            )
            assert rcon._connection.result() == conn

            # Raise error this time
            raise RuntimeError

    connection.disconnect.assert_called_once()
    assert rcon._connection is None, "Connection should be reset to None after error"


async def test_aexit_no_connection(rcon: Rcon) -> None:
    async with rcon:
        rcon._connection = None

    assert rcon._connection is None


async def test_aexit_reconnecting(rcon: Rcon) -> None:
    fut: asyncio.Future[RconConnection] = asyncio.Future()

    async with rcon:
        rcon._connection = fut

    assert rcon._connection is None
    assert fut.cancelled() is True


async def test_aexit_connection_failure(rcon: Rcon) -> None:
    fut: asyncio.Future[RconConnection] = asyncio.Future()
    fut.set_exception(HLLError("Connection failed"))

    async with rcon:
        rcon._connection = fut

    assert rcon._connection is None


async def test_iteration(
    rcon: Rcon,
    connection: mock.Mock,
    connection2: mock.Mock,
) -> None:
    rcon._connection = asyncio.Future()
    rcon._connection.set_result(connection2)

    conn_iter = rcon.__aiter__()
    assert await anext(conn_iter) == connection2
    assert await anext(conn_iter) == connection2

    rcon._connection = None
    assert await anext(conn_iter) == connection


async def test_execute(
    rcon: Rcon,
    connection: mock.Mock,
) -> None:
    command = "command"
    version = 2
    body = "body"
    response = "response"

    connection.execute.return_value = response
    result = await rcon.execute(command, version, body)

    assert result == response
