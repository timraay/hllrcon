import json
from enum import IntEnum
from typing import Any, Self

from hllrcon.exceptions import HLLCommandError


class RconResponseStatus(IntEnum):
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    INTERNAL_ERROR = 500


class RconResponse:
    def __init__(
        self,
        request_id: int,
        command: str,
        version: int,
        status_code: RconResponseStatus,
        status_message: str,
        content_body: str,
    ) -> None:
        self.request_id = request_id
        self.name = command
        self.version = version
        self.status_code = status_code
        self.status_message = status_message
        self.content_body = content_body

    @property
    def content_dict(self) -> dict[str, Any]:
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
        if self.status_code != RconResponseStatus.OK:
            raise HLLCommandError(self.status_code, self.status_message)
