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
    GetMapRotationResponse,
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


class TestIntegratedServer:
    @pytest.fixture(autouse=True)
    def setup_module(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.DEBUG)

    async def test_validate_player_data(self, players: list[GetPlayerResponse]) -> None:
        pass

    async def test_validate_rotation_data(
        self,
        rotation: GetMapRotationResponse,
        sequence: GetMapRotationResponse,
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
        sequence: GetMapRotationResponse,
    ) -> None:
        # Add new map to start of sequence
        new_map_id = "foy_warfare"
        await rcon.add_map_to_sequence(new_map_id, 0)
        new_sequence = await rcon.get_map_sequence()

        # Assert that map was successfully added
        old_map_ids = [entry.id for entry in sequence.maps]
        new_map_ids = [entry.id for entry in new_sequence.maps]
        assert new_map_ids[0] == new_map_id
        assert new_map_ids[1:] == old_map_ids

        # Assert that current index does not change
        assert new_sequence.current_index == sequence.current_index

        # Remove the map we just added
        await rcon.remove_map_from_sequence(0)

        # Assert that sequence is restored to original state
        new_sequence = await rcon.get_map_sequence()
        assert sequence == new_sequence

    async def test_modify_rotation(
        self,
        rcon: Rcon,
        rotation: GetMapRotationResponse,
        sequence: GetMapRotationResponse,
    ) -> None:
        # Add new map to start of rotation
        new_map_id = "foy_warfare"
        await rcon.add_map_to_rotation(new_map_id, 0)
        new_rotation = await rcon.get_map_rotation()
        new_sequence = await rcon.get_map_sequence()

        # Assert that map was successfully added to rotation
        old_map_ids = [entry.id for entry in rotation.maps]
        new_map_ids = [entry.id for entry in new_rotation.maps]
        assert new_map_ids[0] == new_map_id
        assert new_map_ids[1:] == old_map_ids

        # Assert that map was successfully added to sequence
        old_map_ids = [entry.id for entry in sequence.maps]
        new_map_ids = [entry.id for entry in new_sequence.maps]
        assert new_map_ids[0] == new_map_id
        assert new_map_ids[1:] == old_map_ids

        # Assert that current index does not change
        assert rotation.current_index == 0
        assert new_rotation.current_index == 0
        assert new_sequence.current_index == sequence.current_index

        # Remove the map we just added
        await rcon.remove_map_from_rotation(0)

        # Assert that rotation is restored to original state
        new_rotation = await rcon.get_map_rotation()
        new_sequence = await rcon.get_map_sequence()
        assert rotation == new_rotation
        assert sequence == new_sequence
