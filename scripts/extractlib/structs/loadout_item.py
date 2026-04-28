from typing import TYPE_CHECKING

from scripts.extractlib.loader import AssetReference, Model
from scripts.extractlib.objects.blueprint_generated_class import BlueprintGeneratedClass
from scripts.extractlib.types import LocalizationKey

if TYPE_CHECKING:
    from scripts.extractlib.objects.hll_weapon import HLLWeapon


class LoadoutItem(Model):
    weapon: AssetReference[BlueprintGeneratedClass["HLLWeapon"]]
    display_name: LocalizationKey
