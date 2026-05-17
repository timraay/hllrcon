import logging

from pydantic import BaseModel, model_validator

from hllrcon.data.factions import HLLFaction
from hllrcon.data.weapons import HLLWeaponType
from scripts.extract.utils import (
    stringify_enum_member,
    stringify_factions,
    to_method_name,
)

logger = logging.getLogger(__name__)

HLL_WEAPON_CONSTRUCTOR_TEMPLATE = """\
    @class_cached_property
    @classmethod
    def {meth_name}(cls) -> "HLLWeapon":
        \"\"\"*{id}*\"\"\"
        return cls(
            id="{id}",
            name="{name}",
            vehicle_id={vehicle_id},
            factions={factions_str},
            type={weapon_type},
        )"""


class WeaponData(BaseModel):
    meth_name: str = ""
    id: str
    name: str
    vehicle_id: str | None = None
    factions: set[HLLFaction]
    type: HLLWeaponType

    @model_validator(mode="after")
    def set_meth_name(self) -> "WeaponData":
        if not self.meth_name:
            self.meth_name = to_method_name(self.id)
        return self

    @staticmethod
    def merge(*weap_seq: "WeaponData") -> "WeaponData":
        if not weap_seq:
            msg = "At least one WeaponData must be provided"
            raise ValueError(msg)

        if len(weap_seq) == 1:
            return weap_seq[0]

        wd1 = weap_seq[0]
        wd2 = weap_seq[1]

        for prop_name in ("meth_name", "id", "name", "vehicle_id"):
            prop1 = getattr(wd1, prop_name)
            prop2 = getattr(wd2, prop_name)
            if prop1 != prop2:
                logger.warning(
                    "Inconsistent property WeaponData.%s when merging: %s != %s",
                    prop_name,
                    prop1,
                    prop2,
                )

        wd_merged = WeaponData(
            meth_name=wd1.meth_name,
            id=wd1.id,
            name=wd1.name,
            vehicle_id=wd1.vehicle_id,
            factions=wd1.factions.union(wd2.factions),
            type=wd1.type if wd1.type == wd2.type else HLLWeaponType.UNKNOWN,
        )

        return WeaponData.merge(wd_merged, *weap_seq[2:])

    def to_constructor(self) -> str:
        return HLL_WEAPON_CONSTRUCTOR_TEMPLATE.format(
            meth_name=self.meth_name,
            id=self.id,
            name=self.name,
            vehicle_id=f'"{self.vehicle_id}"' if self.vehicle_id else "None",
            factions_str=stringify_factions(self.factions),
            weapon_type=stringify_enum_member(self.type),
        )
