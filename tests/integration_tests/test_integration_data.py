import pytest
from hllrcon import (
    GetServerConfigResponse,
    Layer,
    Rcon,
    __min_server_version__,
)

pytestmark = pytest.mark.asyncio


class TestIntegratedServer:
    async def test_min_server_version_satisfied(
        self,
        server_config: GetServerConfigResponse,
    ) -> None:
        version = int(server_config.build_revision)
        assert version >= __min_server_version__

    async def test_data_layers_all_exist(self, rcon: Rcon) -> None:
        live_layer_ids = set(await rcon.get_available_maps())
        mapped_layer_ids = {layer.id for layer in Layer.all()}
        assert live_layer_ids == mapped_layer_ids

    async def test_data_valid_strongpoints(self, rcon: Rcon) -> None:
        session = await rcon.get_server_session()
        configured_strongpoints = tuple(
            [capture_zone.strongpoint.id for capture_zone in sector.capture_zones]
            for sector in session.find_layer().sectors
        )
        actual_strongpoints = await rcon.get_available_sector_names()
        assert configured_strongpoints == actual_strongpoints
