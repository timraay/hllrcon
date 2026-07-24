from typing import Annotated

from pydantic import Field

from scripts.extractlib.loader import Model, Object
from scripts.extractlib.objects.blueprint_generated_class import BGCReference
from scripts.extractlib.objects.hll_projectile_movement import HLLProjectileMovement
from scripts.extractlib.objects.shooter_damage_type import ShooterDamageType


class ShooterProjectileProperties(Model):
    movement_comp: BGCReference[HLLProjectileMovement]
    projectile_life: float = -1.0
    explosion_damage: float
    explosion_radius: float
    explosion_falloff: float = 0.0
    damage_type: BGCReference[ShooterDamageType]
    explode_at_end_of_life: Annotated[
        bool,
        Field(alias="bExplodeAtEndOfLife"),
    ] = True
    suppression_radius: float
    suppression_amount_flyby: Annotated[
        float,
        Field(alias="SuppressionAmount_Flyby"),
    ] = 0.0
    suppression_amount_explode: Annotated[
        float,
        Field(alias="SuppressionAmount_Explode"),
    ] = 0.0
    suppression_falloff_explode: Annotated[
        float,
        Field(alias="SuppressionFalloff_Explode"),
    ] = 0.0
    suppression_radius_explode: Annotated[
        float,
        Field(alias="SuppressionRadius_Explode"),
    ] = 0.0


class ShooterProjectile(Object[ShooterProjectileProperties]):
    pass
