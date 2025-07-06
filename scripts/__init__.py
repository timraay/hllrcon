import os
from typing import TypedDict

_hll_port = os.getenv("HLL_PORT")

HLL_HOST = os.getenv("HLL_HOST")
HLL_PORT = int(_hll_port) if _hll_port else None
HLL_PASSWORD = os.getenv("HLL_PASSWORD")


class HLLServerCredentials(TypedDict):
    host: str
    port: int
    password: str


HLL_SERVER_CREDENTIALS: HLLServerCredentials | None = (
    {
        "host": HLL_HOST,
        "port": HLL_PORT,
        "password": HLL_PASSWORD,
    }
    if (HLL_HOST and HLL_PORT and HLL_PASSWORD)
    else None
)
