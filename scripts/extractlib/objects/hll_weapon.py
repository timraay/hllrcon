from scripts.extractlib.loader import Model, Object
from scripts.extractlib.objects.data_table import DataTableReference
from scripts.extractlib.structs.loadout_item import HLLLoadoutItem, HLLVLoadoutItem

__all__ = ("HLLWeapon", "HLLWeaponProperties")


class HLLWeaponProperties(Model):
    weapon_meta_data: DataTableReference[HLLLoadoutItem]


class HLLVWeaponProperties(Model):
    weapon_meta_data: DataTableReference[HLLVLoadoutItem]


class HLLWeapon(Object[HLLWeaponProperties]):
    pass


class HLLVWeapon(Object[HLLVWeaponProperties]):
    pass
