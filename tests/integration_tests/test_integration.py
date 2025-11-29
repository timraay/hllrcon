import asyncio
import logging
import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from hllrcon.rcon import Rcon
from hllrcon.responses import (
    GetCommandDetailsResponse,
    GetCommandsResponse,
    GetMapRotationResponseEntry,
    GetPlayerResponse,
    GetServerConfigResponse,
    GetServerSessionResponse,
)
from pydantic import TypeAdapter

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
async def rotation(rcon: Rcon) -> list[GetMapRotationResponseEntry]:
    rotation = await rcon.get_map_rotation()
    return rotation.maps


@pytest_asyncio.fixture
async def sequence(rcon: Rcon) -> list[GetMapRotationResponseEntry]:
    rotation = await rcon.get_map_sequence()
    return rotation.maps


@pytest_asyncio.fixture
async def server_config(rcon: Rcon) -> GetServerConfigResponse:
    return await rcon.get_server_config()


@pytest_asyncio.fixture
async def server_session(rcon: Rcon) -> GetServerSessionResponse:
    return await rcon.get_server_session()


class TestIntegratedServer:
    @pytest.fixture(autouse=True)
    def setup_module(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.DEBUG)

    async def test_validate_player_data(self, players: list[GetPlayerResponse]) -> None:
        pass

    async def test_validate_rotation_data(
        self,
        rotation: list[GetMapRotationResponseEntry],
    ) -> None:
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

        tasks: list[asyncio.Task[GetCommandDetailsResponse]] = []
        async with asyncio.TaskGroup() as tg:
            for command in commands.entries:
                tasks.append(
                    tg.create_task(
                        rcon.get_command_details(command.id),
                    ),
                )
                # Introduce short delay to not overload the server
                await asyncio.sleep(0.002)

        for task in tasks:
            TypeAdapter(GetCommandDetailsResponse).validate_python(task.result())

    async def test_kill_missing_player_returns_false(self, rcon: Rcon) -> None:
        result = await rcon.kill_player("1234567890", "Test reason")
        assert result is False

    async def test_kick_missing_player_returns_false(self, rcon: Rcon) -> None:
        result = await rcon.kick_player("1234567890", "Test reason")
        assert result is False

    async def test_modify_sequence(
        self,
        rcon: Rcon,
        sequence: list[GetMapRotationResponseEntry],
    ) -> None:
        index = len(sequence)

        await rcon.add_map_to_sequence("foy_warfare", index)

        new_sequence = await rcon.get_map_sequence()
        assert new_sequence.maps == [
            *sequence,
            GetMapRotationResponseEntry(
                name="FOY",
                game_mode_name="Warfare",
                time_of_day="Day",
                id="/Game/Maps/foy_warfare",
                position=index,
            ),
        ]

        await rcon.remove_map_from_sequence(index)

        new_sequence = await rcon.get_map_sequence()
        assert new_sequence.maps == sequence
