from scripts.extractlib.loader import Model, Object
from scripts.extractlib.objects.data_table import DataTableReference
from scripts.extractlib.structs.loadout_item import LoadoutItem

__all__ = ("HLLWeapon", "HLLWeaponProperties")


class HLLWeaponProperties(Model):
    weapon_meta_data: DataTableReference[LoadoutItem]


class HLLWeapon(Object[HLLWeaponProperties]):
    pass
