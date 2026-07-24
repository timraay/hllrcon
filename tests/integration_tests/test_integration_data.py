import pytest
from hllrcon import (
    AnyGetServerConfigResponse,
    AnyRcon,
    HLLLayer,
    HLLVLayer,
)
from hllrcon.rcon import HLLRcon, HLLVRcon

from tests.integration_tests.conftest import HLL_GAME

pytestmark = pytest.mark.asyncio


class TestIntegratedServer:
    async def test_min_server_version_satisfied(
        self,
        server_config: AnyGetServerConfigResponse,
    ) -> None:
        min_server_version = (
            HLLRcon.__min_server_version__
            if HLL_GAME == "hll"
            else HLLVRcon.__min_server_version__
        )
        assert server_config.build_revision >= min_server_version

    async def test_data_layers_all_exist(self, rcon: AnyRcon) -> None:
        live_layer_ids = set(await rcon.get_available_maps())
        mapped_layer_ids = {
            layer.id
            for layer in (HLLLayer.all() if HLL_GAME == "hll" else HLLVLayer.all())
        }
        assert live_layer_ids == mapped_layer_ids

    async def test_data_valid_strongpoints(self, rcon: AnyRcon) -> None:
        session = await rcon.get_server_session()
        configured_strongpoints = tuple(
            [capture_zone.strongpoint.id for capture_zone in sector.capture_zones]
            for sector in session.find_layer().sectors
        )
        actual_strongpoints = await rcon.get_available_sector_names()
        assert configured_strongpoints == actual_strongpoints
