import os
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv

ENV_PATH = Path(".env")
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

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
