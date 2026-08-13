from typing import TYPE_CHECKING, Annotated

from pydantic import Field

from scripts.extractlib.loader import Model, Object, ObjectReference
from scripts.extractlib.objects.game_mode_meta_data_asset import GameModeMetaDataAsset

if TYPE_CHECKING:
    from scripts.extractlib.objects.map_meta_data_asset import MapMetaDataAsset


class ScenarioMetaDataAssetProperties(Model):
    scenario_key: str
    game_mode_meta_data_asset: ObjectReference[GameModeMetaDataAsset]
    override_map_id: bool = False
    overridden_map_id: Annotated[str, Field(alias="OverridenMapId")] = ""

    def get_game_mode(self) -> GameModeMetaDataAsset:
        return self.game_mode_meta_data_asset.get(GameModeMetaDataAsset)

    def get_layer_id(self, map_meta: "MapMetaDataAsset") -> str:
        if self.override_map_id:
            return self.overridden_map_id
        return map_meta.properties.get_map_id() + "_" + self.scenario_key


class ScenarioMetaDataAsset(Object[ScenarioMetaDataAssetProperties]):
    pass
