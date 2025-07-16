import itertools
import json
import struct
from typing import Any, ClassVar

from hllrcon.protocol.constants import REQUEST_HEADER_FORMAT


class RconRequest:
    """Represents a RCON request."""

    __request_id_counter: ClassVar["itertools.count[int]"] = itertools.count(start=0)

    def __init__(
        self,
        command: str,
        version: int,
        auth_token: str | None,
        content_body: dict[str, Any] | str = "",
    ) -> None:
        """Initializes a new RCON request.

        Parameters
        ----------
        command : str
            The command to be executed.
        version : int
            The version of the command.
        auth_token : str | None
            The authentication token for the RCON connection.
        content_body : dict[str, Any] | str, optional
            An additional payload to send along with the command. Must be
            JSON-serializable.

        """
        self.name = command
        self.version = version
        self.auth_token = auth_token
        self.content_body = content_body
        self.request_id: int = next(self.__request_id_counter)

    def pack(self) -> tuple[bytes, bytes]:
        """Packs the request into a bytes object.

        Returns
        -------
        tuple[bytes, bytes]
            A tuple containing the header and body of the request.

        """
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
        header = struct.pack(
            REQUEST_HEADER_FORMAT,
            self.request_id,
            len(body_encoded),
        )
        return header, body_encoded
