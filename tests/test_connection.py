import asyncio
from unittest import mock

import pytest
import pytest_asyncio
from hllrcon.connection import RconConnection
from hllrcon.exceptions import HLLConnectionLostError
from hllrcon.protocol.protocol import RconProtocol
from hllrcon.protocol.response import RconResponse, RconResponseStatus


@pytest.fixture
def protocol() -> RconProtocol:
    """Fixture to create a mock RconProtocol."""
    mock_protocol = mock.Mock(spec=RconProtocol)

    def connection_lost(exc: Exception | None) -> None:
        """Mock connection lost method."""
        mock_protocol.is_connected.return_value = False
        mock_protocol.on_connection_lost(exc)

    mock_protocol.is_connected.return_value = True
    mock_protocol.connection_lost = connection_lost
    return mock_protocol


@pytest_asyncio.fixture
async def connection(
    monkeypatch: pytest.MonkeyPatch,
    protocol: RconProtocol,
) -> RconConnection:
    """Fixture to create a mock RconProtocol."""
    monkeypatch.setattr(RconProtocol, "connect", mock.AsyncMock(return_value=protocol))
    return await RconConnection.connect("localhost", 1234, "password")


@pytest.mark.asyncio
async def test_is_connected(connection: RconConnection, protocol: RconProtocol) -> None:
    assert connection.is_connected() is True

    protocol.connection_lost(None)
    assert connection.is_connected() is False


@pytest.mark.asyncio
async def test_disconnect(connection: RconConnection, protocol: mock.Mock) -> None:
    with pytest.raises(asyncio.TimeoutError):
        async with asyncio.timeout(0.1):
            await connection.wait_until_disconnected()

    connection.disconnect()

    protocol.disconnect.assert_called_once()
    protocol.connection_lost(None)

    async with asyncio.timeout(0.1):
        await connection.wait_until_disconnected()


@pytest.mark.asyncio
async def test_execute(
    connection: RconConnection,
    protocol: mock.Mock,
) -> None:
    command = "test_command"
    version = 1
    body = "test_body"
    response = "response"

    protocol.execute.return_value = RconResponse(
        request_id=1,
        command=command,
        version=version,
        status_code=RconResponseStatus.OK,
        status_message="OK",
        content_body="response",
    )

    result = await connection.execute(command, version, body)
    assert result == response

    protocol.connection_lost(None)
    with pytest.raises(HLLConnectionLostError):
        await connection.execute(command, version, body)
