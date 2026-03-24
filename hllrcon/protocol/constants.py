from typing import Final

REQUEST_HEADER_FORMAT: Final[str] = "<III"
RESPONSE_HEADER_FORMAT: Final[str] = "<III"
MAGIC_HEADER_VALUE: Final[int] = 0xDE450508
MAGIC_HEADER_BYTES: Final[bytes] = MAGIC_HEADER_VALUE.to_bytes(4, "little")
