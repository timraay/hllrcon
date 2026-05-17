from pydantic import BaseModel

from hllrcon.data.factions import HLLFaction
from hllrcon.data.weapons import HLLWeaponType
from scripts.extract.utils import (
    stringify_enum_member,
    stringify_factions,
    to_method_name,
)

HLL_WEAPON_CONSTRUCTOR_TEMPLATE = """\
    @class_cached_property
    @classmethod
    def {meth_name}(cls) -> "HLLWeapon":
        \"\"\"*{id}*\"\"\"
        return cls(
            id="{id}",
            name="{name}",
            factions={factions_str},
            type={weapon_type},
        )"""


class WeaponData(BaseModel):
    id: str
    name: str
    factions: set[HLLFaction]
    type: HLLWeaponType

    def to_constructor(self, meth_name: str | None = None) -> str:
        return HLL_WEAPON_CONSTRUCTOR_TEMPLATE.format(
            meth_name=to_method_name(meth_name or self.id),
            id=self.id,
            name=self.name,
            factions_str=stringify_factions(self.factions),
            weapon_type=stringify_enum_member(self.type),
        )
