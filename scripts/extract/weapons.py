import logging
from pathlib import Path
from typing import TypedDict

from pydantic import BaseModel, model_validator

from hllrcon.data.factions import AnyFaction
from hllrcon.data.weapons import WeaponType
from scripts.extract.utils import (
    load_meta,
    save_meta,
    stringify_enum_member,
    stringify_factions,
    to_method_name,
)
from scripts.extractlib.utils import game_switch

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
            magnification={magnification},
        )"""

HLLV_WEAPON_CONSTRUCTOR_TEMPLATE = """\
    @class_cached_property
    @classmethod
    def {meth_name}(cls) -> "HLLVWeapon":
        \"\"\"*{id}*\"\"\"
        return cls(
            id="{id}",
            name="{name}",
            vehicle_id={vehicle_id},
            factions={factions_str},
            type={weapon_type},
            magnification={magnification},
        )"""

_weapon_id_no_metadata_warned: set[str] = set()


class WeaponData(BaseModel):
    meth_name: str = ""
    id: str
    name: str = ""
    vehicle_id: str | None = None
    factions: set[AnyFaction]
    type: WeaponType = WeaponType.UNKNOWN
    magnification: int | None = None

    @model_validator(mode="after")
    def set_meth_name(self) -> "WeaponData":
        metadata = game_switch(HLL_WEAPON_METADATA, HLLV_WEAPON_METADATA)
        meta = metadata.get(self.id)
        if meta is not None:
            self.meth_name = meta.get("meth_name", self.meth_name)
            self.name = meta.get("name", self.name)
            self.type = meta.get("type", self.type)
            self.magnification = meta.get("magnification", self.magnification)
        elif self.id not in _weapon_id_no_metadata_warned:
            logger.warning("No metadata found for weapon ID: %s", self.id)
            _weapon_id_no_metadata_warned.add(self.id)

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

        for prop_name in ("meth_name", "id", "name", "vehicle_id", "magnification"):
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
            type=wd1.type if wd1.type == wd2.type else WeaponType.UNKNOWN,
            magnification=wd1.magnification,
        )

        return WeaponData.merge(wd_merged, *weap_seq[2:])

    def to_constructor(self) -> str:
        template = game_switch(
            HLL_WEAPON_CONSTRUCTOR_TEMPLATE,
            HLLV_WEAPON_CONSTRUCTOR_TEMPLATE,
        )
        return template.format(
            meth_name=self.meth_name,
            id=self.id,
            name=self.name,
            vehicle_id=f'"{self.vehicle_id}"' if self.vehicle_id else "None",
            factions_str=stringify_factions(self.factions, indent=3 * 4).lstrip(),
            weapon_type=stringify_enum_member(self.type),
            magnification=self.magnification,
        )


class WeaponMetaData(TypedDict, total=False):
    meth_name: str
    name: str
    type: WeaponType
    magnification: int


HLL_WEAPON_METADATA_PATH = Path("./scripts/extract/meta/hll/weapons.json")
HLL_WEAPON_METADATA: dict[str, WeaponMetaData] = load_meta(
    HLL_WEAPON_METADATA_PATH,
    WeaponMetaData,
)
save_meta(HLL_WEAPON_METADATA_PATH, WeaponMetaData, HLL_WEAPON_METADATA)

HLLV_WEAPON_METADATA_PATH = Path("./scripts/extract/meta/hllv/weapons.json")
HLLV_WEAPON_METADATA: dict[str, WeaponMetaData] = load_meta(
    HLLV_WEAPON_METADATA_PATH,
    WeaponMetaData,
)
save_meta(HLLV_WEAPON_METADATA_PATH, WeaponMetaData, HLLV_WEAPON_METADATA)
