import asyncio
import concurrent
import concurrent.futures
import contextlib
import logging
from typing import Any
from unittest import mock

import pytest
from hllrcon.connection import RconConnection
from hllrcon.sync.rcon import SyncRcon


@pytest.fixture
def connection() -> RconConnection:
    mock_connection = mock.Mock(spec=RconConnection)
    mock_connection.is_connected.return_value = True
    return mock_connection


@pytest.fixture
def rcon(monkeypatch: pytest.MonkeyPatch, connection: mock.Mock) -> SyncRcon:
    async def get_connection(*_args: Any, **_kwargs: dict[str, Any]) -> RconConnection:  # noqa: ANN401
        return connection

    monkeypatch.setattr("hllrcon.rcon.RconConnection.connect", get_connection)
    return SyncRcon(host="localhost", port=1234, password="password")


def test_basic_usage(rcon: SyncRcon, connection: mock.Mock) -> None:
    with rcon.connect():
        connection.execute.return_value = "pong"
        result = rcon.execute("ping", 1)
        assert result == "pong"


def test_properties(rcon: SyncRcon) -> None:
    assert rcon.host == "localhost"
    assert rcon.port == 1234
    assert rcon.password == "password"
    assert rcon.logger.name == "hllrcon.sync.rcon"
    assert rcon.reconnect_after_failures == 3

    rcon.host = "new_host"
    rcon.port = 4321
    rcon.password = "new_password"
    rcon.logger = logging.getLogger("test")
    rcon.reconnect_after_failures = 5

    assert rcon.host == "new_host"
    assert rcon.port == 4321
    assert rcon.password == "new_password"
    assert rcon.logger.name == "test"
    assert rcon.reconnect_after_failures == 5

    assert rcon._rcon.host == "new_host"
    assert rcon._rcon.port == 4321
    assert rcon._rcon.password == "new_password"
    assert rcon._rcon.logger.name == "test"
    assert rcon._rcon.reconnect_after_failures == 5


def test_is_connected(rcon: SyncRcon, connection: mock.Mock) -> None:
    assert rcon.is_connected() is False, "Should be disconnected initially"

    rcon.wait_until_connected()
    assert rcon.is_connected() is True, "Should be connected after getting connection"

    connection.is_connected.return_value = False
    assert rcon.is_connected() is False, "Should be disconnected after connection loss"


def test_enter_exit(rcon: SyncRcon, connection: mock.Mock) -> None:
    assert rcon._loop is None, "Initial connection should be None"

    with rcon.connect():
        assert rcon._loop is not None, "Loop should be created"
        assert rcon._loop.is_running(), "Loop should be running"

    connection.disconnect.assert_called_once()
    assert rcon._loop is None, "Loop should be reset to None after exit"

    connection.disconnect.reset_mock()

    with contextlib.suppress(RuntimeError), rcon.connect():
        assert rcon._loop is not None, "Loop should be created again"
        assert rcon._loop.is_running(), "Loop should be running again"

        # Raise error this time
        raise RuntimeError

    connection.disconnect.assert_called_once()
    assert rcon._loop is None, "Loop should be reset to None after error"


def test_disconnect(rcon: SyncRcon) -> None:
    rcon.wait_until_connected()
    assert rcon.is_connected()

    rcon.disconnect()
    assert not rcon.is_connected()

    rcon.disconnect()
    assert not rcon.is_connected()


def test_thread_start_failure(monkeypatch: pytest.MonkeyPatch, rcon: SyncRcon) -> None:
    loop_type = type(asyncio.new_event_loop())
    monkeypatch.setattr(loop_type, "run_forever", lambda _: None)
    with pytest.raises(RuntimeError, match="Thread never signalled back"):
        rcon.wait_until_connected()
    assert rcon._loop is None, "Loop should be None after failure"

    def set_loop_none(_: None) -> None:
        rcon._loop = None

    monkeypatch.setattr(loop_type, "run_forever", set_loop_none)
    with pytest.raises(RuntimeError, match="Thread never signalled back"):
        rcon.wait_until_connected()
    assert rcon._loop is None, "Loop should be None after failure"


def test_execute_concurrently(rcon: SyncRcon, connection: mock.Mock) -> None:
    with rcon.connect():
        connection.execute.side_effect = lambda x, *_: {"ping": "pong", "foo": "bar"}[x]
        results = concurrent.futures.wait(
            (
                rcon.execute_concurrently("ping", 1),
                rcon.execute_concurrently("foo", 1),
            ),
        )
        assert {r.result() for r in results.done} == {"pong", "bar"}
