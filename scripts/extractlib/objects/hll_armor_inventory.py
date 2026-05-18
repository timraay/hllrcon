from typing import Annotated

from pydantic import Field

from scripts.extractlib.loader import Model, Object
from scripts.extractlib.objects.blueprint_generated_class import (
    BGCReference,
    BlueprintGeneratedClass,
)
from scripts.extractlib.objects.hll_armor_weapon import (
    HLLArmorWeapon,
    HLLArmorWeaponBallistic,
    HLLArmorWeaponHowitzer,
    HLLArmorWeaponMountedHowitzer,
    HLLArmorWeaponProjectile,
    HLLArmorWeaponReconGun,
    HLLArmorWeaponSmokeScreen,
)


class HLLArmorInventoryPropertiesDefaultInventoryItem(Model):
    owning_seat_index: int
    weapon_class: BGCReference[HLLArmorWeapon]

    def get_weapon(self) -> HLLArmorWeapon:
        weapon_bgc = self.weapon_class.get(BlueprintGeneratedClass)

        if weapon_bgc.super_struct is None:
            msg = f"Expected {weapon_bgc} to have a super struct"
            raise ValueError(msg)

        super_class_name = weapon_bgc.super_struct.object_name
        if super_class_name == "Class'HLLArmourWeapon_Ballistic'":
            weapon = weapon_bgc.get_default_object(HLLArmorWeaponBallistic)
        elif super_class_name == "Class'HLLArmourWeapon_Projectile'":
            weapon = weapon_bgc.get_default_object(HLLArmorWeaponProjectile)
        elif super_class_name == "Class'HLLArmourWeapon_ReconGun'":
            weapon = weapon_bgc.get_default_object(HLLArmorWeaponReconGun)
        elif super_class_name == "Class'HLLArmourWeapon_Howitzer'":
            weapon = weapon_bgc.get_default_object(HLLArmorWeaponHowitzer)
        elif super_class_name == "Class'HLLArmourWeapon_MountedHowitzer'":
            weapon = weapon_bgc.get_default_object(HLLArmorWeaponMountedHowitzer)
        elif super_class_name in {
            "Class'HLLArmourWeapon_SmokeScreen'",
            "Class'HLLArmourWeapon_Smokescreen'",
        }:
            weapon = weapon_bgc.get_default_object(HLLArmorWeaponSmokeScreen)
        else:
            msg = f"Unexpected super struct {super_class_name} for weapon {weapon_bgc}"
            raise ValueError(msg)

        return weapon


class HLLArmorInventoryProperties(Model):
    default_inventory: Annotated[
        list[HLLArmorInventoryPropertiesDefaultInventoryItem],
        Field(default_factory=list),
    ]


class HLLArmorInventory(Object[HLLArmorInventoryProperties]):
    pass
