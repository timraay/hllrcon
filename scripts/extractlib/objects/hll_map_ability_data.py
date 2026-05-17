from typing import Annotated

from pydantic import Field

from scripts.extractlib.loader import AssetReference, Model, Object
from scripts.extractlib.objects.blueprint_generated_class import BlueprintGeneratedClass
from scripts.extractlib.objects.hll_commander_ability import HLLCommanderAbility


class HLLMapAbilityDataAbility(Model):
    ability_class: AssetReference[BlueprintGeneratedClass[HLLCommanderAbility]]
    warfare: Annotated[bool, Field(alias="bWarfare")]
    offensive_defender: Annotated[bool, Field(alias="bOffensiveDefender")]
    offensive_attacker: Annotated[bool, Field(alias="bOffensiveAttacker")]
    conquest_only: Annotated[bool, Field(alias="bConquestOnly")]

    def get_ability(self) -> HLLCommanderAbility | None:
        if self.ability_class.is_none():
            return None

        return self.ability_class.get(
            BlueprintGeneratedClass[HLLCommanderAbility],
        ).get_default_object(HLLCommanderAbility)


class HLLMapAbilityDataProperties(Model):
    abilities: list[HLLMapAbilityDataAbility]


class HLLMapAbilityData(Object[HLLMapAbilityDataProperties]):
    pass
