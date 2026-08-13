import itertools
import logging
from collections.abc import Iterator
from pathlib import Path

from pydantic import BaseModel, model_validator

from hllrcon.data.factions import HLLVFaction
from hllrcon.data.loadouts import HLLVLoadoutItemType
from hllrcon.data.roles import AnyRole, HLLVRole
from scripts import HLLV_METADATA_PATH
from scripts.extract.utils import (
    inject_code,
    stringify_dict,
    stringify_list,
    stringify_role,
    to_method_name,
)
from scripts.extract.weapons import WeaponData
from scripts.extractlib.loader import (
    load_object_from_file,
    local_to_abs_path,
    set_root_path,
)
from scripts.extractlib.objects.blueprint_generated_class import BlueprintGeneratedClass
from scripts.extractlib.objects.data_table import DataTable
from scripts.extractlib.objects.hll_weapon import HLLVWeapon
from scripts.extractlib.structs.loadout_item import (
    HLLVLoadoutItem,
    HLLVLoadoutItemAvailability,
)

logger = logging.getLogger(__name__)

HLLV_LOADOUT_ITEM_CONSTRUCTOR_TEMPLATE = """\
    @class_cached_property
    @classmethod
    def {self.meth_name}(cls) -> "HLLVLoadoutItem":
        return cls(
            id="{self.id}",
            name="{self.name}",
            faction=HLLVFaction.{self.faction.short_name},
            weapon=HLLVWeapon.{self.weapon.meth_name},
            type=HLLVLoadoutItemType.{self.type.name},
            weight={self.weight},
            description_tags={description_tags},
            base_ammo={self.base_ammo},
            max_ammo={self.max_ammo},
            ammo_weight={self.ammo_weight},
            level_requirements={level_requirements},
        )"""

HLLV_LOADOUT_DATA_ROOT_DIR = Path("HLLVietnam/Content/_WFL/Blueprints/Loadouts")
HLLV_LOADOUT_DATA_LOCATIONS: dict[Path, HLLVFaction] = {
    HLLV_LOADOUT_DATA_ROOT_DIR / "DT_WFL_USWeapons": HLLVFaction.US,
    HLLV_LOADOUT_DATA_ROOT_DIR / "DT_NVAWeapons": HLLVFaction.NVA,
}


class LoadoutItemData(BaseModel):
    meth_name: str = ""
    id: str
    name: str
    faction: HLLVFaction
    weapon: WeaponData
    type: HLLVLoadoutItemType
    weight: int
    description_tags: list[str]
    base_ammo: int
    max_ammo: int
    ammo_weight: int
    level_requirements: dict[AnyRole, int]

    @model_validator(mode="after")
    def set_meth_name(self) -> "LoadoutItemData":
        if not self.meth_name:
            self.meth_name = to_method_name(self.id)
        return self

    def to_constructor(self) -> str:
        return HLLV_LOADOUT_ITEM_CONSTRUCTOR_TEMPLATE.format(
            self=self,
            description_tags=stringify_list(
                [f'"{tag}"' for tag in self.description_tags],
                indent=3 * 4,
            ).lstrip(),
            level_requirements=stringify_dict(
                {
                    stringify_role(role): level
                    for role, level in self.level_requirements.items()
                },
                indent=3 * 4,
            ).lstrip(),
        )


def get_loadout_item_level_requirements(
    item: HLLVLoadoutItem,
) -> dict[AnyRole, int]:
    if item.availability == HLLVLoadoutItemAvailability.DISABLED:
        return {}

    level_requirements: dict[AnyRole, int] = {}

    if not item.role_level_requirements:
        level_requirements = dict.fromkeys(
            HLLVRole.all(),
            item.all_roles_level_requirement,
        )

        if (item.all_roles_level_requirement == 0) != (
            item.availability == HLLVLoadoutItemAvailability.ALWAYS
        ):
            logger.warning(
                "Loadout item %s has availability %s"
                " but all_roles_level_requirement %d",
                item.display_name,
                item.availability.name,
                item.all_roles_level_requirement,
            )

    else:
        for level_req in item.role_level_requirements:
            try:
                role = level_req.key.to_hllv_role()
            except ValueError:
                logger.warning(
                    "Ignoring unknown role %s as level requirement for loadout item %s",
                    level_req.key,
                    item.display_name,
                )
                continue
            level_requirements[role] = level_req.value

    return level_requirements


def get_loadout_item_data() -> Iterator[LoadoutItemData]:
    for location, faction in HLLV_LOADOUT_DATA_LOCATIONS.items():
        items = load_object_from_file(
            local_to_abs_path(location),
            0,
            DataTable[HLLVLoadoutItem],
        )

        for name, item in items.rows.items():
            if item.availability == HLLVLoadoutItemAvailability.DISABLED:
                logger.info(
                    "Loadout item %s (%s) is disabled, skipping.",
                    name,
                    faction,
                )
                continue

            weapon = item.weapon.get(
                BlueprintGeneratedClass[HLLVWeapon],
            ).get_default_object(HLLVWeapon)
            weapon_meta = weapon.properties.weapon_meta_data.get(HLLVLoadoutItem)
            weapon_data = WeaponData(
                id=str(weapon_meta.display_name),
                factions={faction},
            )

            yield LoadoutItemData(
                id=name,
                name=str(item.display_name),
                faction=faction,
                weapon=weapon_data,
                type=item.slot_type.to_loadout_item_type(),
                weight=item.item_weight,
                description_tags=[str(tag) for tag in item.item_description_tags],
                base_ammo=item.base_ammo,
                max_ammo=item.max_ammo,
                ammo_weight=item.ammo_weight,
                level_requirements=get_loadout_item_level_requirements(item),
            )


def main() -> None:
    set_root_path(HLLV_METADATA_PATH)

    loadout_item_data = sorted(
        get_loadout_item_data(),
        key=lambda data: data.id,
    )
    loadout_item_constructors = [item.to_constructor() for item in loadout_item_data]
    inject_code(
        Path("hllrcon/data/loadouts.py"),
        "hllv loadout items",
        "\n\n".join(loadout_item_constructors),
    )

    weapon_data = sorted(
        (loadout_item.weapon for loadout_item in loadout_item_data),
        key=lambda w: w.id,
    )
    weapon_ids = itertools.groupby(weapon_data, lambda w: w.id)
    weapons = [WeaponData.merge(*wd_seq) for _, wd_seq in weapon_ids]
    weapons.sort(key=lambda w: w.meth_name)

    """
    # Append suffix to duplicate method names
    for meth_name, weapon_group in itertools.groupby(
        weapons,
        key=lambda w: w.meth_name,
    ):
        for i, weapon in enumerate(weapon_group):
            if i > 0:
                weapon.meth_name = meth_name + "_" + str(i + 1)
    """

    weapon_constructors = [w.to_constructor() for w in weapons]

    inject_code(
        Path("hllrcon/data/weapons.py"),
        "hllv loadout items",
        "\n\n".join(weapon_constructors),
    )


if __name__ == "__main__":
    main()
