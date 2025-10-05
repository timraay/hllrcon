import asyncio
import base64
import binascii
import itertools
import json
from unittest.mock import Mock

import pytest
import pytest_asyncio
from hllrcon.exceptions import (
    HLLAuthError,
    HLLConnectionError,
    HLLConnectionLostError,
    HLLConnectionRefusedError,
    HLLMessageError,
)
from hllrcon.protocol.protocol import RconProtocol
from hllrcon.protocol.request import RconRequest
from hllrcon.protocol.response import RconResponse, RconResponseStatus
from pytest_mock import MockerFixture


@pytest.fixture
def transport(mocker: MockerFixture) -> asyncio.Transport:
    transport: Mock = mocker.Mock(spec=asyncio.Transport)
    transport.is_closing.return_value = False
    return transport


@pytest.fixture
def load_constants(request: pytest.FixtureRequest, mocker: MockerFixture) -> None:
    if marker := request.node.get_closest_marker("do_allow_concurrent_requests"):
        mocker.patch(
            "hllrcon.protocol.protocol.DO_ALLOW_CONCURRENT_REQUESTS",
            bool(marker.args[0]) if marker.args else True,
        )

    if marker := request.node.get_closest_marker("do_pop_v1_xorkey"):
        mocker.patch(
            "hllrcon.protocol.protocol.DO_POP_V1_XORKEY",
            bool(marker.args[0]) if marker.args else True,
        )

    if marker := request.node.get_closest_marker("do_use_request_headers"):
        mocker.patch(
            "hllrcon.protocol.protocol.DO_USE_REQUEST_HEADERS",
            bool(marker.args[0]) if marker.args else True,
        )

    if marker := request.node.get_closest_marker("do_xor_responses"):
        mocker.patch(
            "hllrcon.protocol.protocol.DO_XOR_RESPONSES",
            bool(marker.args[0]) if marker.args else False,
        )


@pytest_asyncio.fixture
async def protocol(
    load_constants: None,  # noqa: ARG001
    transport: asyncio.Transport,
    mocker: MockerFixture,
) -> asyncio.Protocol:
    protocol = RconProtocol(asyncio.get_running_loop(), timeout=1.0)
    protocol.connection_made(transport)
    mocker.patch.object(
        RconRequest,
        "_RconRequest__request_id_counter",
        itertools.count(start=1),
    )
    return protocol


def test_is_connected(protocol: RconProtocol, transport: Mock) -> None:
    assert protocol.is_connected() is True

    transport.is_closing.return_value = True
    assert protocol.is_connected() is False

    protocol._transport = None
    assert protocol.is_connected() is False


@pytest.mark.asyncio
async def test_connect(
    mocker: MockerFixture,
    protocol: RconProtocol,
    transport: Mock,
) -> None:
    mock_create_connection = mocker.patch.object(
        asyncio.get_running_loop(),
        "create_connection",
        return_value=(transport, protocol),
    )

    host = "localhost"
    port = 1234
    password = "password"

    mock_create_connection.side_effect = TimeoutError
    with pytest.raises(
        HLLConnectionError,
        match=f"Address {host} could not be resolved",
    ):
        await protocol.connect(host, port, password)

    mock_create_connection.side_effect = ConnectionRefusedError
    with pytest.raises(
        HLLConnectionRefusedError,
        match=f"The server refused connection over port {port}",
    ):
        await protocol.connect(host, port, password)

    mock_create_connection.side_effect = None
    authenticate = mocker.patch.object(protocol, "authenticate")

    authenticate.side_effect = HLLAuthError
    with pytest.raises(HLLAuthError):
        await protocol.connect(host, port, password)
    assert protocol._transport is None

    authenticate.side_effect = None
    result = await protocol.connect(host, port, password)
    assert result is protocol


def test_disconnect(protocol: RconProtocol, transport: Mock) -> None:
    protocol.disconnect()

    transport.close.assert_called_once()
    assert protocol._transport is None

    protocol.disconnect()


def test_connection_made(protocol: RconProtocol) -> None:
    with pytest.raises(
        TypeError,
        match="Transport must be an instance of asyncio.Transport",
    ):
        protocol.connection_made(Mock(spec=asyncio.BaseTransport))


def test_data_received(
    mocker: MockerFixture,
    protocol: RconProtocol,
) -> None:
    mocker.patch.object(protocol, "_read_from_buffer")

    data1 = b"Some data after xorkey"
    protocol.data_received(data1)

    data2 = b"Even more data"
    protocol.data_received(data2)

    assert protocol._buffer == data1 + data2


def test_read_from_buffer_too_small(
    protocol: RconProtocol,
) -> None:
    data = b"\x01\x02\x03\x04\x05\x06\x07"

    protocol._buffer = data
    protocol._read_from_buffer()
    assert protocol._buffer == data


def test_read_from_buffer_incomplete_packet(
    protocol: RconProtocol,
) -> None:
    data = b"\x01\x00\x00\x00\x05\x00\x00\x00Hell"

    protocol._buffer = data
    protocol._read_from_buffer()
    assert protocol._buffer == data


def test_read_from_buffer_exactly_one_packet(
    mocker: MockerFixture,
    protocol: RconProtocol,
) -> None:
    mock_unpack = mocker.patch(
        "hllrcon.protocol.protocol.RconResponse.unpack",
        autospec=True,
    )
    data = b"\x01\x00\x00\x00\x05\x00\x00\x00Hello"

    waiter: asyncio.Future[RconResponse] = asyncio.Future()
    protocol._waiters[1] = waiter

    protocol._buffer = data
    protocol._read_from_buffer()
    assert protocol._buffer == b""
    assert waiter.result()
    mock_unpack.assert_called_once_with(1, b"Hello")


def test_read_from_buffer_exactly_one_packet_missing_waiter(
    mocker: MockerFixture,
    protocol: RconProtocol,
) -> None:
    mock_unpack = mocker.patch(
        "hllrcon.protocol.protocol.RconResponse.unpack",
        autospec=True,
    )
    data = b"\x01\x00\x00\x00\x05\x00\x00\x00Hello"

    protocol._buffer = data
    protocol._read_from_buffer()
    assert protocol._buffer == b""
    mock_unpack.assert_called_once_with(1, b"Hello")


def test_read_from_buffer_more_than_one_packet(
    mocker: MockerFixture,
    protocol: RconProtocol,
) -> None:
    mock_unpack = mocker.patch(
        "hllrcon.protocol.protocol.RconResponse.unpack",
        autospec=True,
    )
    data = (
        b"\x01\x00\x00\x00\x05\x00\x00\x00Hello"
        b"\x02\x00\x00\x00\x05\x00\x00\x00World"
        b"\x00\x00"
    )

    waiter1: asyncio.Future[RconResponse] = asyncio.Future()
    waiter2: asyncio.Future[RconResponse] = asyncio.Future()
    protocol._waiters[1] = waiter1
    protocol._waiters[2] = waiter2

    protocol._buffer = data
    protocol._read_from_buffer()
    assert protocol._buffer == b"\x00\x00"
    assert waiter1.result()
    assert waiter2.result()
    assert mock_unpack.call_count == 2
    mock_unpack.assert_any_call(1, b"Hello")
    mock_unpack.assert_called_with(2, b"World")


def test_connection_lost_use_request_headers(
    protocol: RconProtocol,
) -> None:
    waiters: dict[int, asyncio.Future[RconResponse]] = {
        1: asyncio.Future(),
        2: asyncio.Future(),
    }
    protocol._waiters = waiters.copy()

    protocol.connection_lost(None)

    assert not protocol.is_connected()
    assert not protocol._waiters
    assert waiters[1].cancelled()
    assert waiters[2].cancelled()


def test_connection_lost_with_exception(
    protocol: RconProtocol,
) -> None:
    waiters: dict[int, asyncio.Future[RconResponse]] = {
        1: asyncio.Future(),
        2: asyncio.Future(),
    }
    protocol._waiters = waiters.copy()

    response = RconResponse(
        request_id=1,
        command="command",
        version=1,
        status_code=RconResponseStatus.OK,
        status_message="OK",
        content_body="foo",
    )
    waiters[1].set_result(response)

    protocol.connection_lost(OSError("Connection error"))

    assert not protocol.is_connected()
    assert not protocol._waiters
    assert waiters[1].result() == response
    assert isinstance(waiters[2].exception(), HLLConnectionLostError)


def test_connection_lost_invokes_callback(
    protocol: RconProtocol,
    mocker: MockerFixture,
) -> None:
    connection_lost_callback = mocker.Mock()
    protocol.on_connection_lost = connection_lost_callback
    protocol.connection_lost(None)
    connection_lost_callback.assert_called_once_with(None)


def test_connection_lost_callback_invocation_failure(
    protocol: RconProtocol,
    mocker: MockerFixture,
) -> None:
    connection_lost_callback = mocker.Mock(side_effect=RuntimeError("Callback failed"))
    protocol.on_connection_lost = connection_lost_callback
    protocol.connection_lost(None)
    connection_lost_callback.assert_called_once_with(None)


def test_xor_single_byte_key(protocol: RconProtocol) -> None:
    protocol.xorkey = b"\x01"
    msg = b"\x00\x01\x02"
    # Each byte XOR 0x01
    expected = bytes([b ^ 0x01 for b in msg])
    assert protocol._xor(msg) == expected


def test_xor_multi_byte_key(protocol: RconProtocol) -> None:
    protocol.xorkey = b"\x01\x02\x03"
    msg = b"\x10\x20\x30\x40\x50\x60"
    # XOR with repeating key
    expected = bytes(
        [
            0x10 ^ 0x01,  # 0
            0x20 ^ 0x02,  # 1
            0x30 ^ 0x03,  # 2
            0x40 ^ 0x01,  # 3
            0x50 ^ 0x02,  # 4
            0x60 ^ 0x03,  # 5
        ],
    )
    assert protocol._xor(msg) == expected


def test_xor_offset(protocol: RconProtocol) -> None:
    protocol.xorkey = b"\x01\x02\x03"
    msg = b"\x10\x20\x30"
    # With offset=1, key index starts at 1
    expected = bytes(
        [
            0x10 ^ 0x02,  # (0+1)%3 = 1
            0x20 ^ 0x03,  # (1+1)%3 = 2
            0x30 ^ 0x01,  # (2+1)%3 = 0
        ],
    )
    assert protocol._xor(msg, offset=1) == expected


def test_xor_roundtrip(protocol: RconProtocol) -> None:
    protocol.xorkey = b"\x0a\x0b\x0c"
    msg = b"SecretMessage"
    encrypted = protocol._xor(msg)
    # XOR again should recover original
    decrypted = protocol._xor(encrypted)
    assert decrypted == msg


def test_xor_length_mismatch_raises(
    protocol: RconProtocol,
    mocker: MockerFixture,
) -> None:
    protocol.xorkey = b"\x01"
    msg = b"\x01\x02"
    # Patch array.array to return wrong length
    mock_array = mocker.patch("array.array")
    mock_array.return_value.tobytes.return_value = b"\x00"
    with pytest.raises(
        ValueError,
        match="XOR operation resulted in a different length",
    ):
        protocol._xor(msg)


def test_xor_warns_on_length_mismatch(
    protocol: RconProtocol,
    mocker: MockerFixture,
) -> None:
    protocol.xorkey = b"\x01"
    msg = b"\x01\x02"
    # Patch array.array to return wrong length and check logger.warning called
    mock_array = mocker.patch("array.array")
    mock_array.return_value.tobytes.return_value = b"\x00"
    mock_logger = mocker.patch.object(protocol.logger, "warning")
    with pytest.raises(
        ValueError,
        match="XOR operation resulted in a different length",
    ):
        protocol._xor(msg)
    mock_logger.assert_called_with(
        "XOR operation resulted in a different length: %s != %s",
        1,
        2,
    )


@pytest.mark.asyncio
async def test_execute_no_connection(
    protocol: RconProtocol,
) -> None:
    protocol.connection_lost(None)
    with pytest.raises(HLLConnectionError, match="Connection is closed"):
        await protocol.execute("command", 1, "body")


def make_response(request_id: int, message: str) -> bytes:
    body = {
        "name": "command",
        "version": 1,
        "statusCode": 200,
        "statusMessage": "OK",
        "contentBody": message,
    }
    body_encoded = json.dumps(body).encode("utf-8")
    return (
        request_id.to_bytes(4, "little")
        + len(body_encoded).to_bytes(4, "little")
        + body_encoded
    )


@pytest.mark.asyncio
async def test_execute(
    protocol: RconProtocol,
    transport: Mock,
) -> None:
    asyncio.get_event_loop().call_later(
        0.1,
        protocol.data_received,
        make_response(0, "response"),
    )
    response = await protocol.execute("command", 1, "body")
    assert response.content_body == "response"
    transport.write.assert_called_once()


@pytest.mark.asyncio
async def test_execute_with_timeout(
    protocol: RconProtocol,
    transport: Mock,
) -> None:
    protocol.timeout = 0.1
    with pytest.raises(TimeoutError):
        await protocol.execute("command", 1, "body")
    assert not protocol._waiters
    transport.write.assert_called_once()


@pytest.mark.asyncio
async def test_execute_concurrently(
    protocol: RconProtocol,
    transport: Mock,
) -> None:
    protocol.timeout = 1.0
    asyncio.get_running_loop().call_later(
        0.5,
        protocol.data_received,
        make_response(1, "response2") + make_response(0, "response1"),
    )
    responses = await asyncio.gather(
        protocol.execute("command1", 1, "body1"),
        protocol.execute("command2", 2, "body2"),
    )
    assert responses[0].content_body == "response1"
    assert responses[1].content_body == "response2"
    assert transport.write.call_count == 2


@pytest.mark.asyncio
async def test_authenticate_success(
    mocker: MockerFixture,
    protocol: RconProtocol,
) -> None:
    # Mock execute to return fake responses for ServerConnect and Login
    xorkey_b64 = base64.b64encode(b"keybytes").decode()
    xorkey_response = mocker.Mock()
    xorkey_response.content_body = xorkey_b64
    xorkey_response.raise_for_status = mocker.Mock()

    auth_token_response = mocker.Mock()
    auth_token_response.content_body = "token123"
    auth_token_response.raise_for_status = mocker.Mock()

    execute = mocker.patch.object(
        protocol,
        "execute",
        side_effect=[xorkey_response, auth_token_response],
    )

    await protocol.authenticate("password")

    execute.assert_has_calls(
        [
            mocker.call("ServerConnect", 2, ""),
            mocker.call("Login", 2, "password"),
        ],
    )
    xorkey_response.raise_for_status.assert_called_once()
    auth_token_response.raise_for_status.assert_called_once()
    assert protocol.xorkey == b"keybytes"
    assert protocol.auth_token == "token123"


@pytest.mark.asyncio
async def test_authenticate_serverconnect_not_string(
    mocker: MockerFixture,
    protocol: RconProtocol,
) -> None:
    # Mock execute to return a non-string content_body for ServerConnect
    xorkey_response = mocker.Mock()
    xorkey_response.content_body = 12345  # Not a string
    xorkey_response.raise_for_status = mocker.Mock()

    execute = mocker.patch.object(protocol, "execute", side_effect=[xorkey_response])

    with pytest.raises(
        HLLMessageError,
        match="ServerConnect response content_body is not a string",
    ):
        await protocol.authenticate("password")

    execute.assert_called_once_with("ServerConnect", 2, "")


@pytest.mark.asyncio
async def test_authenticate_serverconnect_raises_for_status(
    mocker: MockerFixture,
    protocol: RconProtocol,
) -> None:
    # Mock execute to raise for status on ServerConnect
    xorkey_response = mocker.Mock()
    xorkey_response.content_body = "ignored"
    xorkey_response.raise_for_status = mocker.Mock(side_effect=Exception("fail"))

    execute = mocker.patch.object(protocol, "execute", side_effect=[xorkey_response])

    with pytest.raises(Exception, match="fail"):
        await protocol.authenticate("password")

    execute.assert_called_once_with("ServerConnect", 2, "")


@pytest.mark.asyncio
async def test_authenticate_login_raises_for_status(
    mocker: MockerFixture,
    protocol: RconProtocol,
) -> None:
    # Mock execute to raise for status on Login
    xorkey_b64 = base64.b64encode(b"keybytes").decode()
    xorkey_response = mocker.Mock()
    xorkey_response.content_body = xorkey_b64
    xorkey_response.raise_for_status = mocker.Mock()

    auth_token_response = mocker.Mock()
    auth_token_response.content_body = "token123"
    auth_token_response.raise_for_status = mocker.Mock(
        side_effect=Exception("loginfail"),
    )

    mocker.patch.object(
        protocol,
        "execute",
        side_effect=[xorkey_response, auth_token_response],
    )

    with pytest.raises(Exception, match="loginfail"):
        await protocol.authenticate("password")

    assert protocol.xorkey == b"keybytes"
    # auth_token should not be set on failure
    assert protocol.auth_token is None


@pytest.mark.asyncio
async def test_authenticate_xorkey_base64_decode_error(
    mocker: MockerFixture,
    protocol: RconProtocol,
) -> None:
    # Mock execute to return invalid base64 for xorkey
    xorkey_response = mocker.Mock()
    xorkey_response.content_body = "!!!notbase64!!!"
    xorkey_response.raise_for_status = mocker.Mock()

    mocker.patch.object(protocol, "execute", side_effect=[xorkey_response])

    with pytest.raises(binascii.Error):
        await protocol.authenticate("password")
    # xorkey should not be set
    assert protocol.xorkey is None
