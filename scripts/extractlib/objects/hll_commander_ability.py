from typing import Annotated

from pydantic import Field

from scripts.extractlib.loader import Model, Object
from scripts.extractlib.objects.blueprint_generated_class import BGCReference
from scripts.extractlib.objects.hll_vehicle import HLLVehicle
from scripts.extractlib.structs.game_resource import EGameResource
from scripts.extractlib.types import String


class HLLCommanderAbilityProperties(Model):
    resource_category: EGameResource = EGameResource.FUEL
    resource_cost: int = 50
    cooldown_time: float = 600.0
    ability_name: String
    ability_tooltip: String
    action_score_on_execute: str | None = None


class HLLCommanderAbilityDropperPlaneProperties(HLLCommanderAbilityProperties):
    allow_placement_out_of_bounds: Annotated[
        bool,
        Field(alias="bAllowPlacementOutOfBounds"),
    ] = False
    support_rotation: Annotated[bool, Field(alias="bSupportRotation")] = False
    spawn_altitude: float = 0.0
    drop_delay_time: float
    flight_time: float
    plane_speed: float
    plane_altitude: float
    spawn_offset: float
    despawn_offset: float


class HLLCommanderAbilitySpawnVehicleProperties(HLLCommanderAbilityProperties):
    vehicle_class: BGCReference[HLLVehicle]
    ui_sub_category: Annotated[String, Field(alias="UISubCategory")]
    resource_category: EGameResource = EGameResource.FUEL


class HLLCommanderAbilityResourceConversionProperties(HLLCommanderAbilityProperties):
    generated_resource: EGameResource = EGameResource.MUNITIONS


class HLLCommanderAbility(
    Object[
        HLLCommanderAbilityDropperPlaneProperties
        | HLLCommanderAbilitySpawnVehicleProperties
        | HLLCommanderAbilityProperties
    ],
):
    pass
