from typing import Annotated

from pydantic import Field

from hllrcon.data.roles import Role
from scripts.extractlib.loader import Model, Object
from scripts.extractlib.structs.player_role import EPlayerRole


class RoleProgressionAssetLevelUnlock(Model):
    weight_points: int
    enable_additional_ammo: Annotated[bool, Field(alias="bEnableAdditionalAmmo")]
    unlock_secondary_slot: Annotated[bool, Field(alias="bUnlockSecondarySlot")]
    utility_capacity: int
    lethal_capacity: int


class RoleProgressionAssetLevelUnlocks(Model):
    level_unlocks: list[RoleProgressionAssetLevelUnlock]


class RoleProgressionAssetRole(Model):
    key: EPlayerRole
    value: RoleProgressionAssetLevelUnlocks


class RoleProgressionAssetProperties(Model):
    default_progression: RoleProgressionAssetLevelUnlocks
    role_progression: list[RoleProgressionAssetRole]


class RoleProgressionAsset(Object[RoleProgressionAssetProperties]):
    def get_unlocks_for_role(self, role: Role) -> RoleProgressionAssetLevelUnlocks:
        for role_progression in self.properties.role_progression:
            if role_progression.key.to_hllv_role() == role:
                return role_progression.value
        return self.properties.default_progression
