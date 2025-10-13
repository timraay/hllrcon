import asyncio
import contextlib
import logging
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


async def test_logger(rcon: Rcon) -> None:
    assert rcon.logger.name == "hllrcon.rcon"
    rcon.logger = logging.getLogger("test")
    assert rcon.logger.name == "test"
    rcon.logger = None
    assert rcon.logger.name == "hllrcon.rcon"


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


async def test_is_connected(rcon: Rcon, connection: mock.Mock) -> None:
    assert rcon.is_connected() is False, "Should be disconnected initially"

    await rcon.wait_until_connected()
    assert rcon.is_connected() is True, "Should be connected after getting connection"

    connection.is_connected.return_value = False
    assert rcon.is_connected() is False, "Should be disconnected after connection loss"

    rcon._connection = asyncio.Future()
    rcon._connection.set_exception(HLLError("Connection lost"))
    assert rcon.is_connected() is False, "Should be disconnected after exception"

    rcon._connection = asyncio.Future()
    rcon._connection.cancel()
    assert rcon.is_connected() is False, "Should be disconnected after cancelling"


async def test_enter_exit(rcon: Rcon, connection: mock.Mock) -> None:
    assert rcon._connection is None, "Initial connection should be None"

    async with rcon.connect():
        assert rcon._connection is not None, "Connection should be established"

    connection.disconnect.assert_called_once()
    assert rcon._connection is None, "Connection should be reset to None after exit"

    connection.disconnect.reset_mock()

    with contextlib.suppress(RuntimeError):
        async with rcon.connect():
            assert rcon._connection is not None, (
                "Connection should be established again"
            )

            # Raise error this time
            raise RuntimeError

    connection.disconnect.assert_called_once()
    assert rcon._connection is None, "Connection should be reset to None after error"


async def test_aexit_no_connection(rcon: Rcon) -> None:
    async with rcon.connect():
        rcon._connection = None

    assert rcon._connection is None


async def test_aexit_reconnecting(rcon: Rcon) -> None:
    fut: asyncio.Future[RconConnection] = asyncio.Future()

    async with rcon.connect():
        rcon._connection = fut

    assert rcon._connection is None
    assert fut.cancelled() is True


async def test_aexit_connection_failure(rcon: Rcon) -> None:
    fut: asyncio.Future[RconConnection] = asyncio.Future()
    fut.set_exception(HLLError("Connection failed"))

    async with rcon.connect():
        rcon._connection = fut

    assert rcon._connection is None


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


async def test_reconnect_after_failures_parameter() -> None:
    # Test default value
    rcon = Rcon(host="localhost", port=1234, password="password")
    assert rcon.reconnect_after_failures == 3

    # Test custom value
    rcon = Rcon(
        host="localhost",
        port=1234,
        password="password",
        reconnect_after_failures=5,
    )
    assert rcon.reconnect_after_failures == 5

    # Test zero value (disabled)
    rcon = Rcon(
        host="localhost",
        port=1234,
        password="password",
        reconnect_after_failures=0,
    )
    assert rcon.reconnect_after_failures == 0

    # Test negative value gets clamped to zero
    rcon = Rcon(
        host="localhost",
        port=1234,
        password="password",
        reconnect_after_failures=-1,
    )
    assert rcon.reconnect_after_failures == 0


async def test_failure_count_property() -> None:
    rcon = Rcon(host="localhost", port=1234, password="password")

    # Initial failure count should be 0
    assert rcon._failure_count == 0


async def test_failure_count_increment_on_timeout(
    rcon: Rcon,
    connection: mock.Mock,
) -> None:
    # Mock connection.execute to raise TimeoutError
    connection.execute.side_effect = TimeoutError("Connection timeout")

    # Execute command and expect TimeoutError to be raised
    with pytest.raises(TimeoutError, match="Connection timeout"):
        await rcon.execute("test_command", 1, "")

    # Failure count should be incremented
    assert rcon._failure_count == 1

    # Execute another command that times out
    with pytest.raises(TimeoutError, match="Connection timeout"):
        await rcon.execute("test_command", 1, "")

    # Failure count should be incremented again
    assert rcon._failure_count == 2


async def test_failure_count_increment_on_os_error(
    rcon: Rcon,
    connection: mock.Mock,
) -> None:
    # Mock connection.execute to raise OSError
    connection.execute.side_effect = OSError("Network error")

    # Execute command and expect OSError to be raised
    with pytest.raises(OSError, match="Network error"):
        await rcon.execute("test_command", 1, "")

    # Failure count should be incremented
    assert rcon._failure_count == 1


async def test_failure_count_reset_on_disconnect(rcon: Rcon) -> None:
    # Set failure count manually
    rcon._failure_count = 5

    # Disconnect should reset failure count
    rcon.disconnect()
    assert rcon._failure_count == 0


async def test_reconnect_after_failures_disabled(
    monkeypatch: pytest.MonkeyPatch,
    connection: mock.Mock,
) -> None:
    # Create rcon with reconnect_after_failures disabled (0)
    async def get_connection(*_args: Any, **_kwargs: dict[str, Any]) -> RconConnection:  # noqa: ANN401
        return connection

    monkeypatch.setattr("hllrcon.rcon.RconConnection.connect", get_connection)
    rcon = Rcon(
        host="localhost",
        port=1234,
        password="password",
        reconnect_after_failures=0,
    )

    # Mock connection.execute to raise TimeoutError
    connection.execute.side_effect = TimeoutError("Connection timeout")

    # Execute multiple commands that timeout
    for i in range(10):  # Try many times to ensure reconnect doesn't happen
        with pytest.raises(TimeoutError, match="Connection timeout"):
            await rcon.execute("test_command", 1, "")

        # Failure count should keep incrementing
        assert rcon._failure_count == i + 1
        # Connection should still be active (not None)
        assert rcon._connection is not None


async def test_reconnect_after_failures_triggers_disconnect(
    monkeypatch: pytest.MonkeyPatch,
    connection: mock.Mock,
) -> None:
    # Create rcon with reconnect_after_failures = 2
    async def get_connection(*_args: Any, **_kwargs: dict[str, Any]) -> RconConnection:  # noqa: ANN401
        return connection

    monkeypatch.setattr("hllrcon.rcon.RconConnection.connect", get_connection)
    rcon = Rcon(
        host="localhost",
        port=1234,
        password="password",
        reconnect_after_failures=2,
    )

    # Ensure connection is established
    await rcon.wait_until_connected()
    assert rcon._connection is not None

    # Mock connection.execute to raise TimeoutError
    connection.execute.side_effect = TimeoutError("Connection timeout")

    # First failure
    with pytest.raises(TimeoutError, match="Connection timeout"):
        await rcon.execute("test_command", 1, "")
    assert rcon._failure_count == 1
    assert rcon._connection is not None  # Should still be connected

    # Second failure - should trigger disconnect
    with pytest.raises(TimeoutError, match="Connection timeout"):
        await rcon.execute("test_command", 1, "")
    assert rcon._failure_count == 0  # Reset to 0 after disconnect
    assert rcon._connection is None  # Should be disconnected


async def test_failure_count_reset_on_successful_response(
    rcon: Rcon,
    connection: mock.Mock,
) -> None:
    # Set failure count manually
    rcon._failure_count = 5

    # Mock successful response
    connection.execute.return_value = "success"

    # Execute command successfully
    result = await rcon.execute("test_command", 1, "")
    assert result == "success"

    # Failure count should remain unchanged (not reset on success)
    # This is based on the code - it only resets on disconnect
    assert rcon._failure_count == 5


async def test_failure_count_with_different_exception_types(
    rcon: Rcon,
    connection: mock.Mock,
) -> None:
    # Test that only TimeoutError and OSError increment failure count

    # First, test with an exception that should NOT increment failure count
    connection.execute.side_effect = ValueError("Some other error")

    with pytest.raises(ValueError, match="Some other error"):
        await rcon.execute("test_command", 1, "")

    # Failure count should remain 0
    assert rcon._failure_count == 0

    # Now test with TimeoutError
    connection.execute.side_effect = TimeoutError("Timeout")

    with pytest.raises(TimeoutError, match="Timeout"):
        await rcon.execute("test_command", 1, "")

    # Failure count should be incremented
    assert rcon._failure_count == 1

    # Test with OSError
    connection.execute.side_effect = OSError("OS Error")

    with pytest.raises(OSError, match="OS Error"):
        await rcon.execute("test_command", 1, "")

    # Failure count should be incremented again
    assert rcon._failure_count == 2


async def test_reconnect_threshold_exact_match(
    monkeypatch: pytest.MonkeyPatch,
    connection: mock.Mock,
) -> None:
    # Test that disconnect happens exactly when failure count equals threshold
    async def get_connection(*_args: Any, **_kwargs: dict[str, Any]) -> RconConnection:  # noqa: ANN401
        return connection

    monkeypatch.setattr("hllrcon.rcon.RconConnection.connect", get_connection)
    rcon = Rcon(
        host="localhost",
        port=1234,
        password="password",
        reconnect_after_failures=3,
    )

    # Ensure connection is established
    await rcon.wait_until_connected()
    connection.execute.side_effect = TimeoutError("Connection timeout")

    # First two failures should not trigger disconnect
    for i in range(2):
        with pytest.raises(TimeoutError, match="Connection timeout"):
            await rcon.execute("test_command", 1, "")
        assert rcon._failure_count == i + 1
        assert rcon._connection is not None

    # Third failure should trigger disconnect
    with pytest.raises(TimeoutError, match="Connection timeout"):
        await rcon.execute("test_command", 1, "")
    assert rcon._failure_count == 0  # Reset after disconnect
    assert rcon._connection is None
