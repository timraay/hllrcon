from typing import Annotated

from pydantic import Field

from scripts.extractlib.loader import Model, Object
from scripts.extractlib.objects.blueprint_generated_class import BGCReference
from scripts.extractlib.objects.shooter_damage_type import ShooterDamageType


class HLLMortarProjectileProperties(Model):
    incoming_delay: float
    projectile_life: float
    explosion_damage: float
    explosion_radius: float
    damage_type: BGCReference[ShooterDamageType]
    suppression_radius: float
    suppression_amount_flyby: Annotated[float, Field(alias="SuppressionAmount_Flyby")]
    suppression_amount_explode: Annotated[
        float,
        Field(alias="SuppressionAmount_Explode"),
    ]
    suppression_falloff_explode: Annotated[
        float,
        Field(alias="SuppressionFalloff_Explode"),
    ]
    suppression_radius_explode: Annotated[
        float,
        Field(alias="SuppressionRadius_Explode"),
    ]
    show_map_marker: Annotated[bool, Field(alias="bShowMapMarker")]


class HLLMortarProjectile(Object[HLLMortarProjectileProperties]):
    pass
