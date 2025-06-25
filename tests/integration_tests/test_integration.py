import asyncio
import logging
import os
from typing import TypeAlias

import pytest
import pytest_asyncio
from hllrcon.rcon import Rcon
from hllrcon.responses import (
    GetCommandDetailsResponse,
    GetCommandsResponse,
    GetMapRotationResponse,
    GetMapRotationResponseEntry,
    GetPlayerResponse,
    GetPlayersResponse,
    GetServerConfigResponse,
    GetServerSessionResponse,
)
from pydantic import TypeAdapter

Player: TypeAlias = GetPlayerResponse
Map: TypeAlias = GetMapRotationResponseEntry

HLL_HOST = os.getenv("HLL_HOST")
HLL_PORT = os.getenv("HLL_PORT")
HLL_PASSWORD = os.getenv("HLL_PASSWORD")

if not HLL_HOST or not HLL_PORT or not HLL_PASSWORD:
    pytest.skip("HLL environment variables are not set", allow_module_level=True)

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def rcon() -> Rcon:
    return Rcon(
        host=str(HLL_HOST),
        port=int(HLL_PORT or ""),
        password=str(HLL_PASSWORD),
    )


@pytest_asyncio.fixture
async def players(rcon: Rcon) -> list[Player]:
    players = await rcon.get_players()
    TypeAdapter(GetPlayersResponse).validate_python(players)

    if not players["players"]:
        pytest.skip("No players found on the server")

    return players["players"]


@pytest_asyncio.fixture
async def rotation(rcon: Rcon) -> list[Map]:
    rotation = await rcon.get_map_rotation()
    TypeAdapter(GetMapRotationResponse).validate_python(rotation)
    return rotation["mAPS"]


@pytest_asyncio.fixture
async def sequence(rcon: Rcon) -> list[Map]:
    rotation = await rcon.get_map_sequence()
    TypeAdapter(GetMapRotationResponse).validate_python(rotation)
    return rotation["mAPS"]


@pytest_asyncio.fixture
async def server_config(rcon: Rcon) -> GetServerConfigResponse:
    config = await rcon.get_server_config()
    TypeAdapter(GetServerConfigResponse).validate_python(config)
    return config


@pytest_asyncio.fixture
async def server_session(rcon: Rcon) -> GetServerSessionResponse:
    session = await rcon.get_server_session()
    TypeAdapter(GetServerSessionResponse).validate_python(session)
    return session


class TestIntegratedServer:
    @pytest.fixture(autouse=True)
    def setup_module(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.DEBUG)

    async def test_validate_player_data(self, players: list[Player]) -> None:
        pass

    async def test_validate_rotation_data(self, rotation: list[Map]) -> None:
        pass

    async def test_validate_server_session_data(
        self,
        server_session: GetServerSessionResponse,
    ) -> None:
        pass

    async def test_validate_server_config_data(
        self,
        server_config: GetServerConfigResponse,
    ) -> None:
        pass

    async def test_validate_client_reference_data(self, rcon: Rcon) -> None:
        commands = await rcon.get_commands()
        TypeAdapter(GetCommandsResponse).validate_python(commands)

        details = await asyncio.gather(
            *(
                rcon.get_command_details(command["iD"])
                for command in commands["entries"]
            ),
        )
        TypeAdapter(list[GetCommandDetailsResponse]).validate_python(details)

    async def test_kill_missing_player_returns_false(self, rcon: Rcon) -> None:
        result = await rcon.kill_player("1234567890", "Test reason")
        assert result is False

    async def test_kick_missing_player_returns_false(self, rcon: Rcon) -> None:
        result = await rcon.kick_player("1234567890", "Test reason")
        assert result is False

    async def test_modify_sequence(self, rcon: Rcon, sequence: list[Map]) -> None:
        index = len(sequence)

        await rcon.add_map_to_sequence("foy_warfare", index)

        new_sequence = await rcon.get_map_sequence()
        assert new_sequence["mAPS"] == [
            *sequence,
            Map(
                name="FOY",
                gameMode="Warfare",
                timeOfDay="Day",
                iD="/Game/Maps/foy_warfare",
                position=index,
            ),
        ]

        await rcon.remove_map_from_sequence(index)

        new_sequence = await rcon.get_map_sequence()
        assert new_sequence["mAPS"] == sequence
