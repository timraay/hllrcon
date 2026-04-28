from collections.abc import Iterable
from typing import Annotated

from pydantic import AfterValidator, Field

from hllrcon.data.roles import HLLRole
from scripts.extractlib.loader import Model, Object
from scripts.extractlib.objects.data_table import DataTableReference
from scripts.extractlib.structs.loadout_item import LoadoutItem
from scripts.extractlib.types import LocalizationKey


class HLLTeamLoadoutsPropertiesLoadoutItem(Model):
    loadout_item: DataTableReference[LoadoutItem]
    initial_clips: Annotated[int, AfterValidator(lambda v: max(v, 1))]
    maximum_clips: int


class HLLTeamLoadoutsPropertiesLoadout(Model):
    display_name: Annotated[
        LocalizationKey,
        Field(validation_alias="LoadoutDisplayName"),
    ]
    level_requirement: int
    role_level_requirement: int
    loadout_items: list[HLLTeamLoadoutsPropertiesLoadoutItem]


class HLLTeamLoadoutsProperties(Model):
    faction: str | None = None

    rifleman: list[HLLTeamLoadoutsPropertiesLoadout]
    assault: list[HLLTeamLoadoutsPropertiesLoadout]
    automatic_rifleman: list[HLLTeamLoadoutsPropertiesLoadout]
    medic: list[HLLTeamLoadoutsPropertiesLoadout]
    spotter: list[HLLTeamLoadoutsPropertiesLoadout]
    support: list[HLLTeamLoadoutsPropertiesLoadout]
    machine_gunner: list[HLLTeamLoadoutsPropertiesLoadout]
    anti_tank: list[HLLTeamLoadoutsPropertiesLoadout]
    engineer: list[HLLTeamLoadoutsPropertiesLoadout]
    officer: list[HLLTeamLoadoutsPropertiesLoadout]
    sniper: list[HLLTeamLoadoutsPropertiesLoadout]
    crewman: list[HLLTeamLoadoutsPropertiesLoadout]
    tank_commander: list[HLLTeamLoadoutsPropertiesLoadout]
    army_commander: list[HLLTeamLoadoutsPropertiesLoadout]
    artillery_observer: list[HLLTeamLoadoutsPropertiesLoadout]
    artillery_engineer: list[HLLTeamLoadoutsPropertiesLoadout]
    artillery_support: list[HLLTeamLoadoutsPropertiesLoadout]

    def items(self) -> Iterable[tuple[HLLRole, list[HLLTeamLoadoutsPropertiesLoadout]]]:
        yield HLLRole.ARMY_COMMANDER, self.army_commander
        yield HLLRole.OFFICER, self.officer
        yield HLLRole.RIFLEMAN, self.rifleman
        yield HLLRole.ASSAULT, self.assault
        yield HLLRole.AUTOMATIC_RIFLEMAN, self.automatic_rifleman
        yield HLLRole.MEDIC, self.medic
        yield HLLRole.SUPPORT, self.support
        yield HLLRole.MACHINE_GUNNER, self.machine_gunner
        yield HLLRole.ANTI_TANK, self.anti_tank
        yield HLLRole.ENGINEER, self.engineer
        yield HLLRole.TANK_COMMANDER, self.tank_commander
        yield HLLRole.CREWMAN, self.crewman
        yield HLLRole.ARTILLERY_OBSERVER, self.artillery_observer
        yield HLLRole.OPERATOR, self.artillery_engineer
        yield HLLRole.GUNNER, self.artillery_support
        yield HLLRole.SPOTTER, self.spotter
        yield HLLRole.SNIPER, self.sniper


class HLLTeamLoadouts(Object[HLLTeamLoadoutsProperties]):
    pass
