import logging
from pathlib import Path

from pydantic import BaseModel

from hllrcon.data.roles import HLLVRole, Role
from scripts import HLLV_METADATA_PATH
from scripts.extract.utils import indent_text, inject_code, stringify_list
from scripts.extractlib.loader import (
    load_object_from_file,
    local_to_abs_path,
    set_root_path,
)
from scripts.extractlib.objects.role_progression_asset import RoleProgressionAsset

logger = logging.getLogger(__name__)

HLLV_ROLE_PROGRESSION_PATH = Path(
    "HLLVietnam/Content/_WFL/Blueprints/Loadouts/DA_RoleProgression",
)
HLLV_ROLE_PROGRESSION_CONSTRUCTOR_TEMPLATE = """\
progression={entries}"""
HLLV_ROLE_PROGRESSION_ENTRY_CONSTRUCTOR_TEMPLATE = """\
HLLVRoleProgression(
    level={self.level},
    max_weight={self.max_weight},
    secondary_slot_unlocked={self.secondary_slot_unlocked},
    extra_ammo_unlocked={self.extra_ammo_unlocked},
    lethal_slots={self.lethal_slots},
    utility_slots={self.utility_slots},
)"""


class RoleProgressionEntryData(BaseModel):
    level: int
    max_weight: int
    secondary_slot_unlocked: bool
    extra_ammo_unlocked: bool
    lethal_slots: int
    utility_slots: int

    def to_constructor(self) -> str:
        return HLLV_ROLE_PROGRESSION_ENTRY_CONSTRUCTOR_TEMPLATE.format(self=self)


class RoleProgressionData(BaseModel):
    role: Role
    progression: list[RoleProgressionEntryData]

    def to_constructor(self) -> str:
        progression_entries = [entry.to_constructor() for entry in self.progression]
        return indent_text(
            HLLV_ROLE_PROGRESSION_CONSTRUCTOR_TEMPLATE.format(
                entries=stringify_list(progression_entries),
            ),
            3 * 4,
        )


def get_role_progression_data() -> list[RoleProgressionData]:
    progression_asset = load_object_from_file(
        local_to_abs_path(HLLV_ROLE_PROGRESSION_PATH),
        0,
        RoleProgressionAsset,
    )

    progression_data: list[RoleProgressionData] = []

    for role in HLLVRole.all():
        role_unlocks = progression_asset.get_unlocks_for_role(role)

        progression_data.append(
            RoleProgressionData(
                role=role,
                progression=[
                    RoleProgressionEntryData(
                        level=i + 1,
                        max_weight=level_unlock.weight_points,
                        secondary_slot_unlocked=level_unlock.unlock_secondary_slot,
                        extra_ammo_unlocked=level_unlock.enable_additional_ammo,
                        lethal_slots=level_unlock.lethal_capacity,
                        utility_slots=level_unlock.utility_capacity,
                    )
                    for i, level_unlock in enumerate(role_unlocks.level_unlocks)
                ],
            ),
        )

    return progression_data


def main() -> None:
    set_root_path(HLLV_METADATA_PATH)

    for role_progression in get_role_progression_data():
        inject_code(
            Path("hllrcon/data/roles.py"),
            f"hllv progression {role_progression.role.name}",
            role_progression.to_constructor(),
        )


if __name__ == "__main__":
    main()
