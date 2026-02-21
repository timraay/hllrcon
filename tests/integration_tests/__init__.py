import asyncio
import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from hllrcon.rcon import Rcon

HLL_HOST = os.getenv("HLL_HOST")
HLL_PORT = os.getenv("HLL_PORT")
HLL_PASSWORD = os.getenv("HLL_PASSWORD")

if not HLL_HOST or not HLL_PORT or not HLL_PASSWORD:
    pytest.skip("HLL environment variables are not set", allow_module_level=True)


@pytest_asyncio.fixture(scope="function")
async def rcon() -> AsyncGenerator[Rcon]:
    rcon = Rcon(
        host=str(HLL_HOST),
        port=int(HLL_PORT or ""),
        password=str(HLL_PASSWORD),
    )
    await asyncio.sleep(0.1)
    async with rcon.connect():
        yield rcon
