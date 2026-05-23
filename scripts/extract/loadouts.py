import itertools
import logging
from collections.abc import Iterator
from pathlib import Path

from pydantic import BaseModel, model_validator

from hllrcon.data.factions import HLLFaction
from hllrcon.data.roles import HLLRole
from scripts import HLL_METADATA_PATH
from scripts.extract.utils import (
    inject_code,
    stringify_list,
    stringify_role,
    to_method_name,
)
from scripts.extract.weapons import WeaponData
from scripts.extractlib.loader import local_to_abs_path, set_root_path
from scripts.extractlib.objects.blueprint_generated_class import BlueprintGeneratedClass
from scripts.extractlib.objects.hll_team_loadouts import HLLTeamLoadouts
from scripts.extractlib.objects.hll_weapon import HLLWeapon
from scripts.extractlib.structs.loadout_item import HLLLoadoutItem
from scripts.extractlib.utils import find_objects_in_dir

logger = logging.getLogger(__name__)

HLL_LOADOUT_OUTPUT_PATH = Path("hllrcon/data/loadouts.py")
HLL_LOADOUT_CONSTRUCTOR_TEMPLATE = """\
    @class_cached_property
    @classmethod
    def {self.meth_name}(cls) -> "HLLLoadout":
        return cls(
            name="{self.name}",
            faction=HLLFaction.{self.faction.short_name},
            role={role},
            requires_level={self.requires_level},
            items={items},
        )"""
HLL_LOADOUT_ITEM_CONSTRUCTOR_TEMPLATE = """\
HLLLoadoutItem(
    weapon=HLLWeapon.{self.weapon.meth_name},
    ammo={self.ammo},
)"""


class LoadoutItemData(BaseModel):
    weapon: WeaponData
    ammo: int

    def to_constructor(self) -> str:
        return HLL_LOADOUT_ITEM_CONSTRUCTOR_TEMPLATE.format(self=self)


class LoadoutData(BaseModel):
    meth_name: str = ""
    name: str
    faction: HLLFaction
    role: HLLRole
    requires_level: int
    items: list[LoadoutItemData]

    @model_validator(mode="after")
    def set_meth_name(self) -> "LoadoutData":
        if not self.meth_name:
            faction_name = self.faction.short_name
            role_name = (
                self.role.pretty_name.replace(" ", "_").replace("-", "_").upper()
            )
            self.meth_name = to_method_name(
                f"{faction_name}_{role_name}_{self.name}",
            )
        return self

    def to_constructor(self) -> str:
        items = [item.to_constructor() for item in self.items]
        return HLL_LOADOUT_CONSTRUCTOR_TEMPLATE.format(
            self=self,
            role=stringify_role(self.role),
            items=stringify_list(items, indent=3 * 4).lstrip(),
        )

    def get_weapons(self) -> list[WeaponData]:
        return [item.weapon for item in self.items]


LOADOUTS_DIR = Path("HLL/Content/Blueprints/Loadouts")


def get_loadouts() -> Iterator[HLLTeamLoadouts]:
    for loadouts, _ in find_objects_in_dir(
        local_to_abs_path(LOADOUTS_DIR, add_ext=False),
        lambda obj: obj.type == "HLLTeamLoadouts",
        obj_type=HLLTeamLoadouts,
        glob_pattern="**/*Loadouts.json",
    ):
        yield loadouts


def get_loadout_data() -> Iterator[LoadoutData]:
    for loadouts in get_loadouts():
        try:
            faction = loadouts.properties.faction.to_hll_faction()
        except ValueError:
            logger.warning(
                "Skipping loadouts with unknown faction: %s",
                loadouts.properties.faction,
            )
            continue

        for role, loadouts_for_role in loadouts.properties.items():
            for loadout in loadouts_for_role:
                items: list[LoadoutItemData] = []
                for item in loadout.loadout_items:
                    weapon = (
                        item.loadout_item.get(HLLLoadoutItem)
                        .weapon.get(BlueprintGeneratedClass[HLLWeapon])
                        .get_default_object(HLLWeapon)
                    )
                    weapon_meta = weapon.properties.weapon_meta_data.get(HLLLoadoutItem)
                    item_name = str(weapon_meta.display_name)
                    items.append(
                        LoadoutItemData(
                            weapon=WeaponData(
                                id=item_name,
                                name=item_name,
                                factions={faction},
                            ),
                            ammo=item.initial_clips,
                        ),
                    )

                yield LoadoutData(
                    name=str(loadout.display_name),
                    faction=faction,
                    role=role,
                    requires_level=loadout.role_level_requirement,
                    items=items,
                )


def main() -> None:
    set_root_path(HLL_METADATA_PATH)

    loadouts = sorted(
        get_loadout_data(),
        key=lambda data: (
            data.faction.id * 10000 + data.role.id * 100 + data.requires_level
        ),
    )
    loadout_constructors = [data.to_constructor() for data in loadouts]

    inject_code(
        HLL_LOADOUT_OUTPUT_PATH,
        "hll loadouts",
        "\n\n".join(loadout_constructors),
    )

    weapon_data = sorted(
        (weapon for loadout in loadouts for weapon in loadout.get_weapons()),
        key=lambda w: w.id,
    )
    weapon_ids = itertools.groupby(weapon_data, lambda w: w.id)
    weapons = [WeaponData.merge(*wd_seq) for _, wd_seq in weapon_ids]
    weapons.sort(key=lambda w: w.meth_name)

    # Append suffix to duplicate method names
    for meth_name, weapon_group in itertools.groupby(
        weapons,
        key=lambda w: w.meth_name,
    ):
        for i, weapon in enumerate(weapon_group):
            if i > 0:
                weapon.meth_name = meth_name + "_" + str(i + 1)

    weapon_constructors = [w.to_constructor() for w in weapons]

    inject_code(
        Path("hllrcon/data/weapons.py"),
        "hll loadouts",
        "\n\n".join(weapon_constructors),
    )


if __name__ == "__main__":
    main()
