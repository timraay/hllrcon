from collections.abc import Iterator
from typing import Annotated

from pydantic import Field

from hllrcon.data.game_modes import AnyGameMode, HLLVGameMode
from hllrcon.data.maps import CardinalDirection
from scripts.extractlib.loader import Model, Object, ObjectReference
from scripts.extractlib.objects.layout_meta_data_asset import LayoutMetaDataAsset
from scripts.extractlib.objects.scenario_meta_data_asset import ScenarioMetaDataAsset
from scripts.extractlib.structs.faction import EFaction
from scripts.extractlib.types import String


class MapMetaDataAssetProperties(Model):
    map_friendly_name: String
    map_id: str
    axis_faction: EFaction
    allies_faction: EFaction
    increment_map_achievement: Annotated[bool, Field(alias="bIncrementMapAchievement")]
    map_achievement_stat: str
    scenarios: list[ObjectReference[ScenarioMetaDataAsset]]

    def get_scenarios(self) -> Iterator[ScenarioMetaDataAsset]:
        for scenario_ref in self.scenarios:
            yield scenario_ref.get(ScenarioMetaDataAsset)

    def get_scenario(self, game_mode: AnyGameMode) -> ScenarioMetaDataAsset:
        for scenario in self.get_scenarios():
            gm = scenario.properties.get_game_mode()
            gm_id = gm.properties.get_game_mode_id()
            if gm_id.lower() == game_mode.id.lower():
                return scenario

        msg = f"Map {self.map_id} has no scenarios with a {game_mode.id} game mode"
        raise ValueError(msg)

    def get_warfare_scenario(self) -> ScenarioMetaDataAsset:
        return self.get_scenario(HLLVGameMode.WARFARE)

    def get_direction(self) -> CardinalDirection:
        scenario = self.get_warfare_scenario()
        game_mode = scenario.properties.get_game_mode()
        layout = game_mode.properties.layout_meta_data_asset.get(
            LayoutMetaDataAsset,
        )
        return layout.properties.allies_orientation.to_cardinal_direction()


class MapMetaDataAsset(Object[MapMetaDataAssetProperties]):
    pass
