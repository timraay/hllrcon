import array
import asyncio
import base64
import itertools
import logging
import struct
from collections.abc import Callable
from typing import Any, Self

from typing_extensions import override

from hllrcon.exceptions import (
    HLLAuthError,
    HLLConnectionError,
    HLLConnectionLostError,
    HLLConnectionRefusedError,
    HLLMessageError,
)
from hllrcon.protocol.constants import RESPONSE_HEADER_FORMAT
from hllrcon.protocol.request import RconRequest
from hllrcon.protocol.response import RconResponse

DEFAULT_LOGGER = logging.getLogger(__name__)


class RconProtocol(asyncio.Protocol):
    """Implementation of the RCON protocol for Hell Let Loose.

    This class extends the TCP protocol to handle communication with a
    Hell Let Loose server using the RCON protocol, including sending commands
    and receiving responses.

    Example usage:
    ```python
    conn = await RconProtocol.connect(host=..., port=..., password=...)
    response = await conn.execute(
        command="KickPlayer",
        version=2,
        content_body={
            "PlayerId": "75670000000000000",
            "Reason": "Violation of rules",
        },
    )
    conn.disconnect()
    ```

    You likely do not want to use this class directly. Instead, use `RconConnection`
    which provides a higher-level interface for interacting with the game server.
    """

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        timeout: float | None = None,
        logger: logging.Logger | None = None,
        on_connection_lost: Callable[[Exception | None], Any] | None = None,
    ) -> None:
        """Initialize a RconProtocol instance.

        Do not initialize this class directly. Use the `connect` class method instead.

        Parameters
        ----------
        loop : asyncio.AbstractEventLoop
            The event loop to use for asynchronous operations.
        timeout : float | None, optional
            The timeout for operations, in seconds. If None, no timeout is set.
        logger : logging.Logger | None, optional
            A logger instance for logging messages. If None, a default logger is used.
        on_connection_lost : Callable[[Exception | None], Any] | None, optional
            A callback function to call when the connection is lost. It receives an
            exception if the connection was lost due to an error, or None if it was
            closed gracefully.

        """
        self._transport: asyncio.Transport | None = None
        self._buffer: bytes = b""

        self._waiters: dict[int, asyncio.Future[RconResponse]] = {}

        self.loop = loop
        self.timeout = timeout
        self.logger = logger or DEFAULT_LOGGER
        self.on_connection_lost = on_connection_lost

        self.xorkey: bytes | None = None
        self.auth_token: str | None = None

        self._counter = itertools.count(start=0)

    @classmethod
    async def connect(
        cls: type[Self],
        host: str,
        port: int,
        password: str,
        timeout: float | None = 10,
        loop: asyncio.AbstractEventLoop | None = None,
        logger: logging.Logger | None = None,
        on_connection_lost: Callable[[Exception | None], Any] | None = None,
    ) -> Self:
        """Establish a connection to the Hell Let Loose server.

        This method creates a connection to the specified server and authenticates
        using the provided password. It returns an instance of the RconProtocol.

        Parameters
        ----------
        host : str
            The hostname or IP address of the Hell Let Loose server.
        port : int
            The port number on which the RCON server is listening.
        password : str
            The RCON password for authentication.
        timeout : float | None, optional
            The timeout for the connection attempt, in seconds, by default 10.
        loop : asyncio.AbstractEventLoop | None, optional
            The event loop to use for asynchronous operations, by default None. If None,
            `asyncio.get_running_loop()` is used.
        logger : logging.Logger | None, optional
            A logger instance for logging messages, by default None. If None,
            `logging.getLogger(__name__)` is used.
        on_connection_lost : Callable[[Exception | None], Any] | None, optional
            An optional callback function to call when the connection is lost, by
            default None.

        Raises
        ------
        HLLConnectionError
            The address and port could not be resolved.
        HLLConnectionRefusedError
            The server refused the connection.
        HLLAuthError
            The provided password is incorrect.

        """
        loop = loop or asyncio.get_running_loop()

        def protocol_factory() -> Self:  # type: ignore[type-var, misc]
            return cls(  # pragma: no cover
                loop=loop,
                timeout=timeout,
                logger=logger,
                on_connection_lost=on_connection_lost,
            )

        try:
            self: Self
            _, self = await asyncio.wait_for(
                loop.create_connection(protocol_factory, host=host, port=port),
                timeout=15,
            )
        except TimeoutError:
            msg = f"Address {host} could not be resolved"
            raise HLLConnectionError(msg) from None
        except ConnectionRefusedError:
            msg = f"The server refused connection over port {port}"
            raise HLLConnectionRefusedError(msg) from None

        self.logger.info("Connected!")

        try:
            await self.authenticate(password)
        except HLLAuthError:
            self.disconnect()
            raise

        return self

    def disconnect(self) -> None:
        """Close the connection to the Hell Let Loose server.

        If the connection is already closed, this method does nothing.
        """
        if self._transport:
            self._transport.close()
        self._transport = None

    def is_connected(self) -> bool:
        """Check if the protocol is connected to the server.

        Returns
        -------
        bool
            True if the protocol is connected, False otherwise.

        """
        return self._transport is not None and not self._transport.is_closing()

    @override
    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self.logger.info("Connection made! Transport: %s", transport)
        if not isinstance(transport, asyncio.Transport):
            msg = "Transport must be an instance of asyncio.Transport"
            raise TypeError(msg)
        self._transport = transport

    @override
    def data_received(self, data: bytes) -> None:
        self.logger.debug("Incoming: (%s) %s", self._xor(data).count(b"\t"), data[:10])

        self._buffer += data
        self._read_from_buffer()

    def _read_from_buffer(self) -> None:
        pkt_id: int
        pkt_len: int

        # Read header
        header_len = struct.calcsize(RESPONSE_HEADER_FORMAT)
        if len(self._buffer) < header_len:
            self.logger.debug(
                "Buffer too small (%s < %s)",
                len(self._buffer),
                header_len,
            )
            return
        pkt_id, pkt_len = struct.unpack(
            RESPONSE_HEADER_FORMAT,
            self._buffer[:header_len],
        )
        pkt_size = header_len + pkt_len
        self.logger.debug("pkt_id = %s, pkt_len = %s", pkt_id, pkt_len)

        # Check whether whole packet is on buffer
        if len(self._buffer) >= pkt_size:
            # Read packet data from buffer
            decoded_body = self._xor(self._buffer[header_len:pkt_size])
            self.logger.debug("Unpacking: %s", decoded_body)
            pkt = RconResponse.unpack(pkt_id, decoded_body)
            self._buffer = self._buffer[pkt_size:]

            # Respond to waiter
            waiter = self._waiters.pop(pkt_id, None)
            if not waiter:
                self.logger.warning(
                    "No waiter for packet with ID %s, %s",
                    pkt_id,
                    self._waiters,
                )
            else:
                waiter.set_result(pkt)

            # Repeat if buffer is not empty; Another complete packet might be on it
            if self._buffer:
                self._read_from_buffer()

    @override
    def connection_lost(self, exc: Exception | None) -> None:
        self._transport = None

        waiters = list(self._waiters.values())
        self._waiters.clear()

        if exc:
            self.logger.warning("Connection lost: %s", exc)
            for waiter in waiters:
                if not waiter.done():
                    waiter.set_exception(HLLConnectionLostError(str(exc)))

        else:
            self.logger.info("Connection closed")
            for waiter in waiters:
                waiter.cancel()

        if self.on_connection_lost:
            try:
                self.on_connection_lost(exc)
            except Exception:
                self.logger.exception("Failed to invoke on_connection_lost hook")

    def _xor(self, message: bytes, offset: int = 0) -> bytes:
        """Encrypt or decrypt a message using the XOR key provided by the server.

        Parameters
        ----------
        message : bytes
            The message to encrypt or decrypt.
        offset : int, optional
            The offset to apply to the XOR key. Defaults to 0.

        Returns
        -------
        bytes
            The encrypted or decrypted message.

        """
        if not self.xorkey:
            return message

        n = [
            c ^ self.xorkey[(i + offset) % len(self.xorkey)]
            for i, c in enumerate(message)
        ]

        res = array.array("B", n).tobytes()
        if len(res) != len(message):
            self.logger.warning(
                "XOR operation resulted in a different length: %s != %s",
                len(res),
                len(message),
            )
            msg = "XOR operation resulted in a different length"
            raise ValueError(msg)

        return res

    async def execute(
        self,
        command: str,
        version: int,
        content_body: dict[str, Any] | str = "",
    ) -> RconResponse:
        """Execute a RCON command.

        Sends a request to the server and waits for a response.

        Parameters
        ----------
        command : str
            The command to execute on the server.
        version : int
            The version of the command.
        content_body : dict[str, Any] | str, optional
            An additional payload to send along with the command. Must be
            JSON-serializable.

        Raises
        ------
        HLLConnectionError
            The connection was closed
        HLLCommandError
            The server failed to execute the command
        HLLMessageError
            The server returned an unexpected response

        """
        if not self._transport:
            msg = "Connection is closed"
            raise HLLConnectionError(msg)

        # Create request
        request = RconRequest(
            command=command,
            version=version,
            auth_token=self.auth_token,
            content_body=content_body,
        )
        # Temporary solution to ensure each connection uses its own counter
        request.request_id = next(self._counter)

        # Send request
        header, body = request.pack()
        message = header + self._xor(body)
        self.logger.debug("Writing: %s", header + body)
        self._transport.write(message)

        try:
            # Create waiter for response
            waiter: asyncio.Future[RconResponse] = self.loop.create_future()
            self._waiters[request.request_id] = waiter

            # Wait for response
            response = await asyncio.wait_for(waiter, timeout=self.timeout)
            self.logger.debug(
                "Response: (%s) %s",
                response.name,
                response.content_body,
            )
            return response
        finally:
            # Cleanup waiter
            waiter.cancel()
            self._waiters.pop(request.request_id, None)

    async def authenticate(self, password: str) -> None:
        """Authenticate with the Hell Let Loose server.

        Parameters
        ----------
        password : str
            The RCON password to authenticate with.

        Raises
        ------
        HLLAuthError
            The provided password is incorrect.

        """
        self.logger.debug("Waiting to login...")

        xorkey_resp = await self.execute("ServerConnect", 2, "")
        xorkey_resp.raise_for_status()
        self.logger.info("Received xorkey")

        if not isinstance(xorkey_resp.content_body, str):
            msg = "ServerConnect response content_body is not a string"
            raise HLLMessageError(msg)
        self.xorkey = base64.b64decode(xorkey_resp.content_body)

        auth_token_resp = await self.execute("Login", 2, password)
        auth_token_resp.raise_for_status()
        self.logger.info("Received auth token, successfully authenticated")

        self.auth_token = auth_token_resp.content_body
