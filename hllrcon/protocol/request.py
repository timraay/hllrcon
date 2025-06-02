import itertools
import json
import struct
from typing import Any, ClassVar

from hllrcon.protocol.constants import DO_USE_REQUEST_HEADERS, HEADER_FORMAT


class RconRequest:
    __request_id_counter: ClassVar["itertools.count[int]"] = itertools.count(start=1)

    def __init__(
        self,
        command: str,
        version: int,
        auth_token: str | None,
        content_body: dict[str, Any] | str = "",
    ) -> None:
        self.name = command
        self.version = version
        self.auth_token = auth_token
        self.content_body = content_body
        self.request_id: int = next(self.__request_id_counter)

    def pack(self) -> bytes:
        body = {
            "authToken": self.auth_token or "",
            "version": self.version,
            "name": self.name,
            "contentBody": (
                self.content_body
                if isinstance(self.content_body, str)
                else json.dumps(self.content_body, separators=(",", ":"))
            ),
        }
        body_encoded = json.dumps(body, separators=(",", ":")).encode()
        if DO_USE_REQUEST_HEADERS:
            header = struct.pack(HEADER_FORMAT, self.request_id, len(body_encoded))
            return header + body_encoded
        return body_encoded
