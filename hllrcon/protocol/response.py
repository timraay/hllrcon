import json
from enum import IntEnum
from typing import Any, Self

from hllrcon.exceptions import HLLCommandError


class RconResponseStatus(IntEnum):
    """Enumeration of RCON response status codes."""

    OK = 200
    """The request was successful."""

    BAD_REQUEST = 400
    """The request was invalid."""

    UNAUTHORIZED = 401
    """Insufficient or invalid authorization."""

    INTERNAL_ERROR = 500
    """An internal server error occurred."""


class RconResponse:
    """Represents a RCON response."""

    def __init__(
        self,
        request_id: int,
        command: str,
        version: int,
        status_code: RconResponseStatus,
        status_message: str,
        content_body: str,
    ) -> None:
        """Initializes a new RCON response.

        Parameters
        ----------
        request_id : int
            The ID of the request this response corresponds to.
        command : str
            The command that was executed.
        version : int
            The version of the command.
        status_code : RconResponseStatus
            The status code of the response.
        status_message : str
            A message describing the status of the response.
        content_body : str
            The body of the response, potentially JSON-deserializable.

        """
        self.request_id = request_id
        self.name = command
        self.version = version
        self.status_code = status_code
        self.status_message = status_message
        self.content_body = content_body

    @property
    def content_dict(self) -> dict[str, Any]:
        """JSON-deserialize the content body of the response.

        Raises
        ------
        json.JSONDecodeError
            The content body could not be deserialized.
        TypeError
            The deserialized content is not a dictionary.

        Returns
        -------
        dict[str, Any]
            The deserialized content body as a dictionary.

        """
        parsed_content = json.loads(self.content_body)
        if not isinstance(parsed_content, dict):
            msg = f"Expected JSON content to be a dict, got {type(parsed_content)}"
            raise TypeError(msg)
        return parsed_content

    def __str__(self) -> str:
        content: str | dict[str, Any]
        try:
            content = self.content_dict
        except (json.JSONDecodeError, TypeError):
            content = self.content_body

        return f"{self.status_code} {self.name} {content}"

    @classmethod
    def unpack(cls, request_id: int, body_encoded: bytes) -> Self:
        """Unpacks a RCON response from its bytes representation.

        Parameters
        ----------
        request_id : int
            The ID of the request this response corresponds to.
        body_encoded : bytes
            The encoded body of the response, which is expected to be a JSON string.

        Returns
        -------
        RconResponse
            The unpacked RCON response object.

        """
        body = json.loads(body_encoded)
        return cls(
            request_id=request_id,
            command=str(body["name"]),
            version=int(body["version"]),
            status_code=RconResponseStatus(int(body["statusCode"])),
            status_message=str(body["statusMessage"]),
            content_body=body["contentBody"],
        )

    def raise_for_status(self) -> None:
        """Raises an exception if the response status is not OK.

        Raises
        ------
        HLLCommandError
            The response status code is not `RconResponseStatus.OK`.

        """
        if self.status_code != RconResponseStatus.OK:
            raise HLLCommandError(self.status_code, self.status_message)
