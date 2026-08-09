from typing import Annotated

from pydantic import Field

from scripts.extractlib.loader import AssetReference, Model, Object, ObjectReference
from scripts.extractlib.objects.blueprint_generated_class import (
    BGCReference,
    BlueprintGeneratedClass,
)
from scripts.extractlib.objects.hll_map_ability_data import HLLMapAbilityData
from scripts.extractlib.objects.layout_meta_data_asset import LayoutMetaDataAsset
from scripts.extractlib.structs.sector_type import ESectorType
from scripts.extractlib.structs.team import ETeam
from scripts.extractlib.structs.warfare_objective import EWarfareObjective
from scripts.extractlib.types import String


class GameModeMetaDataAssetSectorDefinition(Model):
    name: String
    type: ESectorType
    warfare_type: EWarfareObjective
    munitions: int
    fuel: int
    manpower: int
    initial_owner: ETeam
    contains_river: Annotated[bool, Field(alias="bContainsRiver")]


class GameModeMetaDataAssetProperties(Model):
    game_mode: BGCReference
    game_mode_name: String | None = None
    attacking_team: ETeam = ETeam.NONE
    data_layers_to_load: list[AssetReference]
    layout_meta_data_asset: ObjectReference[LayoutMetaDataAsset]
    sector_definitions: list[GameModeMetaDataAssetSectorDefinition]
    axis_ability_data: ObjectReference[HLLMapAbilityData]
    allies_ability_data: ObjectReference[HLLMapAbilityData]
    update_game_mode_achievement_stat: Annotated[
        bool,
        Field(alias="bUpdateGameModeAchievementStat"),
    ] = False
    game_mode_achievement_stat: str = ""

    def get_layout(self) -> LayoutMetaDataAsset:
        return self.layout_meta_data_asset.get(LayoutMetaDataAsset)

    def get_game_mode_id(self) -> str:
        bgc_name = self.game_mode.get(BlueprintGeneratedClass).name
        return (
            bgc_name.removeprefix("HLL_GameMode_")
            .removeprefix("BP_")
            .removesuffix("_C")
            .removesuffix("_GameMode")
            .lower()
        )


class GameModeMetaDataAsset(Object[GameModeMetaDataAssetProperties]):
    pass
