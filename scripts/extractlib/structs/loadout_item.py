from enum import StrEnum
from typing import TYPE_CHECKING

from hllrcon.data.loadouts import HLLVLoadoutItemType
from scripts.extractlib.loader import AssetReference, Model
from scripts.extractlib.objects.blueprint_generated_class import BlueprintGeneratedClass
from scripts.extractlib.structs.player_role import EPlayerRole
from scripts.extractlib.types import String

if TYPE_CHECKING:
    from scripts.extractlib.objects.hll_weapon import HLLVWeapon, HLLWeapon


class HLLLoadoutItem(Model):
    weapon: AssetReference[BlueprintGeneratedClass["HLLWeapon"]]
    display_name: String


class HLLVLoadoutEquipmentType(StrEnum):
    PRIMARY = "ELoadoutEquipmentType::ET_Primary"
    UTILITY = "ELoadoutEquipmentType::ET_Utility"
    LETHAL = "ELoadoutEquipmentType::ET_Lethal"
    VERSATILE = "ELoadoutEquipmentType::ET_Versatile"
    LOCKED_ITEM = "ELoadoutEquipmentType::ET_LockedItem"
    MAX = "ELoadoutEquipmentType::ET_MAX"

    def to_loadout_item_type(self) -> HLLVLoadoutItemType:
        return HLLVLoadoutItemType[self.name]


class HLLVLoadoutItemAvailability(StrEnum):
    ALWAYS = "ELoadoutAvailability::LA_Always"
    UNLOCKABLE = "ELoadoutAvailability::LA_Unlockable"
    DISABLED = "ELoadoutAvailability::LA_Disabled"


class HLLVLoadoutItemRoleLevelRequirement(Model):
    key: EPlayerRole
    value: int


class HLLVLoadoutItem(Model):
    weapon: AssetReference[BlueprintGeneratedClass["HLLVWeapon"]]
    slot_type: HLLVLoadoutEquipmentType
    item_weight: int
    # parent_item
    base_ammo: int
    max_ammo: int
    ammo_weight: int
    availability: HLLVLoadoutItemAvailability
    role_level_requirements: list[HLLVLoadoutItemRoleLevelRequirement]
    all_roles_level_requirement: int
    display_name: String
    item_description_tags: list[String]
