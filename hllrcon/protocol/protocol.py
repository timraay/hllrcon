import array
import asyncio
import base64
import contextlib
import logging
import struct
from collections import deque
from collections.abc import Callable
from typing import Any, Self

from hllrcon.exceptions import (
    HLLAuthError,
    HLLConnectionError,
    HLLConnectionLostError,
    HLLConnectionRefusedError,
    HLLMessageError,
)
from hllrcon.protocol.constants import (
    DO_ALLOW_CONCURRENT_REQUESTS,
    DO_POP_V1_XORKEY,
    DO_USE_REQUEST_HEADERS,
    HEADER_FORMAT,
)
from hllrcon.protocol.request import RconRequest
from hllrcon.protocol.response import RconResponse


class RconProtocol(asyncio.Protocol):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        timeout: float | None = None,
        logger: logging.Logger | None = None,
        on_connection_lost: Callable[[Exception | None], Any] | None = None,
    ) -> None:
        self._transport: asyncio.Transport | None = None
        self._buffer: bytes = b""

        if DO_USE_REQUEST_HEADERS:
            self._waiters: dict[int, asyncio.Future[RconResponse]] = {}
        else:
            self._queue: deque[asyncio.Future[RconResponse]] = deque()

        if not DO_ALLOW_CONCURRENT_REQUESTS:
            self._lock = asyncio.Lock()

        if DO_POP_V1_XORKEY:
            self._seen_v1_xorkey: bool = False

        self.loop = loop
        self.timeout = timeout
        self.logger = logger or logging.getLogger()
        self.on_connection_lost = on_connection_lost

        self.xorkey: bytes | None = None
        self.auth_token: str | None = None

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
        loop = loop or asyncio.get_running_loop()

        def protocol_factory() -> Self:  # type: ignore[type-var, misc]
            return cls(  # pragma: no cover
                loop=loop,
                timeout=timeout,
                logger=logger,
                on_connection_lost=on_connection_lost,
            )

        try:
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
        if self._transport:
            self._transport.close()
        self._transport = None

    def is_connected(self) -> bool:
        return self._transport is not None and not self._transport.is_closing()

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self.logger.info("Connection made! Transport: %s", transport)
        if not isinstance(transport, asyncio.Transport):
            msg = "Transport must be an instance of asyncio.Transport"
            raise TypeError(msg)
        self._transport = transport

    def data_received(self, data: bytes) -> None:
        self.logger.debug("Incoming: (%s) %s", self._xor(data).count(b"\t"), data[:10])

        if DO_POP_V1_XORKEY and not self._seen_v1_xorkey:
            self.logger.info("Ignoring V1 XOR-key: %s", data[:4])
            self._seen_v1_xorkey = True
            data = data[4:]
            if not data:
                return

        self._buffer += data
        self._read_from_buffer()

    def _read_from_buffer(self) -> None:
        pkt_id: int
        pkt_len: int

        # Read header
        header_len = struct.calcsize(HEADER_FORMAT)
        if len(self._buffer) < header_len:
            self.logger.debug(
                "Buffer too small (%s < %s)",
                len(self._buffer),
                header_len,
            )
            return
        pkt_id, pkt_len = struct.unpack(HEADER_FORMAT, self._buffer[:header_len])
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
            if DO_USE_REQUEST_HEADERS:
                waiter = self._waiters.pop(pkt_id, None)
                if not waiter:
                    self.logger.warning(
                        "No waiter for packet with ID %s, %s",
                        pkt_id,
                        self._waiters,
                    )
                else:
                    waiter.set_result(pkt)
            elif not self._queue:
                self.logger.warning("No waiter for packet with ID %s", pkt_id)
            else:
                waiter = self._queue.popleft()
                waiter.set_result(pkt)

            # Repeat if buffer is not empty; Another complete packet might be on it
            if self._buffer:
                self._read_from_buffer()

    def connection_lost(self, exc: Exception | None) -> None:
        self._transport = None

        if DO_USE_REQUEST_HEADERS:
            waiters = list(self._waiters.values())
            self._waiters.clear()
        else:
            waiters = list(self._queue)
            self._queue.clear()

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
        """Encrypt or decrypt a message using the XOR key provided by the server."""
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

        if not DO_ALLOW_CONCURRENT_REQUESTS:
            await self._lock.acquire()

        try:
            # Send request
            packed = request.pack()
            message = self._xor(packed)
            self.logger.debug("Writing: %s", packed)
            self._transport.write(message)

            try:
                # Create waiter for response
                waiter: asyncio.Future[RconResponse] = self.loop.create_future()
                if DO_USE_REQUEST_HEADERS:
                    self._waiters[request.request_id] = waiter
                else:
                    self._queue.append(waiter)

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

                if DO_USE_REQUEST_HEADERS:
                    self._waiters.pop(request.request_id, None)
                else:
                    with contextlib.suppress(ValueError):
                        self._queue.remove(waiter)
        finally:
            if not DO_ALLOW_CONCURRENT_REQUESTS:
                self._lock.release()

    async def authenticate(self, password: str) -> None:
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
