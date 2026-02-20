import asyncio
import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from hllrcon import (
    GetMapRotationResponse,
    GetPlayerResponse,
    GetServerConfigResponse,
    GetServerSessionResponse,
    Rcon,
)

HLL_HOST = os.getenv("HLL_HOST")
HLL_PORT = os.getenv("HLL_PORT")
HLL_PASSWORD = os.getenv("HLL_PASSWORD")

if not HLL_HOST or not HLL_PORT or not HLL_PASSWORD:
    pytest.skip("HLL environment variables are not set", allow_module_level=True)

pytestmark = pytest.mark.asyncio


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


@pytest_asyncio.fixture
async def players(rcon: Rcon) -> list[GetPlayerResponse]:
    players = await rcon.get_players()

    if not players.players:
        pytest.skip("No players found on the server")

    return players.players


@pytest_asyncio.fixture
async def rotation(rcon: Rcon) -> GetMapRotationResponse:
    return await rcon.get_map_rotation()


@pytest_asyncio.fixture
async def sequence(rcon: Rcon) -> GetMapRotationResponse:
    return await rcon.get_map_sequence()


@pytest_asyncio.fixture
async def server_config(rcon: Rcon) -> GetServerConfigResponse:
    return await rcon.get_server_config()


@pytest_asyncio.fixture
async def server_session(rcon: Rcon) -> GetServerSessionResponse:
    return await rcon.get_server_session()
