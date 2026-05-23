from typing import Annotated

from pydantic import Field

from scripts.extractlib.loader import Model, Object
from scripts.extractlib.objects.blueprint_generated_class import BGCReference
from scripts.extractlib.objects.shooter_damage_type import ShooterDamageType


class HLLProjectileBulletProperties(Model):
    muzzle_velocity: float = 0.0  # TODO: Default
    mass_g: float = 10.0  # TODO: Default
    diameter_mm: Annotated[float, Field(alias="DiameterMM")]
    form_factor: float = 0  # TODO: Default
    max_penetrations: int = 1  # TODO: Default
    penetration_power: int = 1  # TODO: Default
    max_flight_time: float
    damage_type: BGCReference[ShooterDamageType]
    damage_curve: Model  # TODO: Add damage curve
    suppress_scale: float = 1.0


class HLLProjectileBullet(Object[HLLProjectileBulletProperties]):
    pass
