from enum import StrEnum
from typing import Annotated

from pydantic import Field

from scripts.extractlib.loader import Model, Object
from scripts.extractlib.types import String


class EHLLArmorPenetration(StrEnum):
    VERY_LOW = "EHLLArmourPenetration::AP_VeryLow"
    LOW = "EHLLArmourPenetration::AP_Low"
    MEDIUM = "EHLLArmourPenetration::AP_Medium"
    HIGH = "EHLLArmourPenetration::AP_High"
    VERY_HIGH = "EHLLArmourPenetration::AP_VeryHigh"


class EHLLArmorDamageType(StrEnum):
    HE = "EHLLArmourDamageType::ADT_HE"


class EHLLDamageType(StrEnum):
    SMALL_BULLET = "EHLLDamageType::DT_SmallBullet"
    MEDIUM_BULLET = "EHLLDamageType::DT_MediumBullet"
    LARGE_BULLET = "EHLLDamageType::DT_LargeBullet"
    EXPLOSION = "EHLLDamageType::DT_Explosion"
    FIRE = "EHLLDamageType::DT_Fire"


class ShooterDamageTypeProperties(Model):
    damage_type_text: String
    point_damage_radius: float
    armor_penetration: Annotated[
        EHLLArmorPenetration | None,
        Field(alias="ArmourPenetration"),
    ] = None
    armor_damage_type: Annotated[
        EHLLArmorDamageType | None,
        Field(alias="ArmourDamageType"),
    ] = None
    radial_armor_penetration: Annotated[
        EHLLArmorPenetration | None,
        Field(alias="RadialArmourPenetration"),
    ] = None
    radial_armor_damage_type: Annotated[
        EHLLArmorDamageType | None,
        Field(alias="RadialArmourDamageType"),
    ] = None
    damage_type: EHLLDamageType


class ShooterDamageType(Object[ShooterDamageTypeProperties]):
    pass
