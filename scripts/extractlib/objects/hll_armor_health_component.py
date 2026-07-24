from typing import Annotated

from pydantic import AliasPath, Field

from scripts.extractlib.loader import Model, Object


class HLLArmorHealthComponentPropertiesArmorInfo(Model):
    hull_max_health: Annotated[
        float,
        Field(alias=AliasPath("HealthData", "MaxHealth")),
    ] = 200.0
    turret_max_health: Annotated[
        float,
        Field(alias=AliasPath("HealthData", "MaxHealth[1]")),
    ] = 200.0
    tracks_max_health: Annotated[
        float,
        Field(alias=AliasPath("HealthData", "MaxHealth[2]")),
    ] = 200.0
    engine_max_health: Annotated[
        float,
        Field(alias=AliasPath("HealthData", "MaxHealth[3]")),
    ] = 200.0


class HLLArmorHealthComponentProperties(Model):
    armor_info: Annotated[
        HLLArmorHealthComponentPropertiesArmorInfo,
        Field(
            alias="ArmourInfo",
            default_factory=HLLArmorHealthComponentPropertiesArmorInfo,
        ),
    ]
    # compartments
    death_explosion_damage: float = 0.0
    death_explosion_radius: float = 0.0
    death_explosion_suppression: float = 0.0
    death_explosion_suppression_radius: float = 0.0
    on_death_moral_cost: int = 1  # TODO: Verify (Daimler CAN)


class HLLArmorHealthComponent(Object[HLLArmorHealthComponentProperties]):
    pass
