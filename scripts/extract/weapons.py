# ruff: noqa: RUF001

import logging
from typing import TypedDict

from pydantic import BaseModel, model_validator

from hllrcon.data.factions import Faction
from hllrcon.data.weapons import WeaponType
from scripts.extract.utils import (
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
    factions: set[Faction]
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
            factions_str=stringify_factions(self.factions),
            weapon_type=stringify_enum_member(self.type),
            magnification=self.magnification,
        )


class WeaponMetaData(TypedDict, total=False):
    meth_name: str
    name: str
    type: WeaponType
    magnification: int


HLL_WEAPON_METADATA: dict[str, WeaponMetaData] = {
    "M1 GARAND": {
        "name": "M1 Garand",
        "type": WeaponType.SEMI_AUTO_RIFLE,
    },
    "M1 CARBINE": {
        "name": "M1 Carbine",
        "type": WeaponType.SEMI_AUTO_RIFLE,
    },
    "M1A1 THOMPSON": {
        "name": "M1A1 Thompson",
        "type": WeaponType.SUBMACHINE_GUN,
    },
    "M3 GREASE GUN": {
        "name": "M3 Grease Gun",
        "type": WeaponType.SUBMACHINE_GUN,
    },
    "M1918A2 BAR": {
        "name": "M1918A2 BAR",
        "type": WeaponType.ASSAULT_RIFLE,
    },
    "BROWNING M1919": {
        "name": "M1919 Browning",
        "type": WeaponType.MACHINE_GUN,
    },
    "M1903 SPRINGFIELD": {
        "name": "M1903 Springfield",
        "type": WeaponType.BOLT_ACTION_RIFLE,
        "magnification": 4,
    },
    "M97 TRENCH GUN": {
        "name": "M97 Trench Gun",
        "type": WeaponType.SHOTGUN,
    },
    "COLT M1911": {
        "name": "Colt M1911",
        "type": WeaponType.PISTOL,
    },
    "M3 KNIFE": {
        "name": "M3 Knife",
        "type": WeaponType.MELEE,
    },
    "SATCHEL": {
        "name": "Satchel Charge",
        "type": WeaponType.SATCHEL,
    },
    "MK2 GRENADE": {
        "name": "Mk 2 Grenade",
        "type": WeaponType.GRENADE,
    },
    "M2 FLAMETHROWER": {
        "name": "M2 Flamethrower",
        "type": WeaponType.FLAMETHROWER,
    },
    "BAZOOKA": {
        "name": "Bazooka",
        "type": WeaponType.ROCKET_LAUNCHER,
    },
    "M2 AP MINE": {
        "name": "M2 AP Mine",
        "type": WeaponType.AP_MINE,
    },
    "M1A1 AT MINE": {
        "name": "M1A1 AT Mine",
        "type": WeaponType.AT_MINE,
    },
    "FLARE GUN": {
        "name": "Flare Gun",
        "type": WeaponType.RECON_FLARE,
    },
    "57MM CANNON [M1 57mm]": {
        "name": "57mm Cannon",
    },
    "155MM HOWITZER [M114]": {
        "name": "155mm Howitzer",
    },
    "M8 Greyhound": {},
    "Stuart M5A1": {},
    "Sherman M4A3(75)W": {},
    "Sherman M4A3E2": {},
    "Sherman M4A3E2(76)": {},
    "GMC CCKW 353 (Supply)": {},
    "GMC CCKW 353 (Transport)": {},
    "M3 Half-track": {},
    "Jeep Willys": {},
    "M4A3 (105mm)": {},
    "M6 37mm [M8 Greyhound]": {
        "name": "37mm Cannon",
    },
    "COAXIAL M1919 [M8 Greyhound]": {
        "name": "M1919 Browning",
    },
    "37MM CANNON [Stuart M5A1]": {
        "name": "37mm Cannon",
    },
    "COAXIAL M1919 [Stuart M5A1]": {
        "name": "M1919 Browning",
    },
    "HULL M1919 [Stuart M5A1]": {
        "name": "M1919 Browning",
    },
    "75MM CANNON [Sherman M4A3(75)W]": {
        "name": "75mm Cannon",
    },
    "COAXIAL M1919 [Sherman M4A3(75)W]": {
        "name": "M1919 Browning",
    },
    "HULL M1919 [Sherman M4A3(75)W]": {
        "name": "M1919 Browning",
    },
    "75MM M3 GUN [Sherman M4A3E2]": {
        "name": "75mm Cannon",
    },
    "COAXIAL M1919 [Sherman M4A3E2]": {
        "name": "M1919 Browning",
    },
    "HULL M1919 [Sherman M4A3E2]": {
        "name": "M1919 Browning",
    },
    "76MM M1 GUN [Sherman M4A3E2(76)]": {
        "name": "76mm Cannon",
    },
    "COAXIAL M1919 [Sherman M4A3E2(76)]": {
        "name": "M1919 Browning",
    },
    "HULL M1919 [Sherman M4A3E2(76)]": {
        "name": "M1919 Browning",
    },
    "M2 Browning [M3 Half-track]": {
        "name": "M2 Browning",
    },
    "105MM HOWITZER [M4A3 (105mm)]": {
        "name": "105mm Howitzer",
    },
    "COAXIAL M1919 [M4A3 (105mm)]": {
        "name": "M1919 Browning",
    },
    "HULL M1919 [M4A3 (105mm)]": {
        "name": "M1919 Browning",
    },
    "57MM CANNON": {
        "name": "57mm Cannon",
    },
    "155MM HOWITZER": {
        "name": "155mm Howitzer",
    },
    "76MM M1 GUN": {
        "name": "76mm Cannon",
    },
    "75MM M3 GUN": {
        "name": "75mm Cannon",
    },
    "75MM CANNON": {
        "name": "75mm Cannon",
    },
    "37MM CANNON": {
        "name": "37mm Cannon",
    },
    "M6 37MM": {
        "name": "37mm Cannon",
    },
    "COAXIAL M1919": {
        "name": "M1919 Browning",
    },
    "HULL M1919": {
        "name": "M1919 Browning",
    },
    "M2 Browning": {
        "name": "M2 Browning",
        "type": WeaponType.MOUNTED_MG,
    },
    "KARABINER 98K": {
        "name": "Karabiner 98k",
        "type": WeaponType.BOLT_ACTION_RIFLE,
    },
    "GEWEHR 43": {
        "name": "G43",
        "type": WeaponType.SEMI_AUTO_RIFLE,
    },
    "STG44": {
        "name": "STG44",
        "type": WeaponType.ASSAULT_RIFLE,
    },
    "FG42": {
        "name": "FG42",
        "type": WeaponType.ASSAULT_RIFLE,
    },
    "MP40": {
        "name": "MP40",
        "type": WeaponType.SUBMACHINE_GUN,
    },
    "MG34": {
        "name": "MG34",
        "type": WeaponType.MACHINE_GUN,
    },
    "MG42": {
        "name": "MG42",
        "type": WeaponType.MACHINE_GUN,
    },
    "FLAMMENWERFER 41": {
        "name": "Flammenwerfer 41",
        "type": WeaponType.FLAMETHROWER,
    },
    "KARABINER 98K x8": {
        "name": "Karabiner 98k",
        "type": WeaponType.BOLT_ACTION_RIFLE,
        "magnification": 8,
    },
    "FG42 x4": {
        "name": "FG42",
        "type": WeaponType.SEMI_AUTO_RIFLE,
        "magnification": 4,
    },
    "LUGER P08": {
        "name": "Luger P08",
        "type": WeaponType.PISTOL,
    },
    "WALTHER P38": {
        "name": "Walther P38",
        "type": WeaponType.PISTOL,
    },
    "FELDSPATEN": {
        "name": "Feldspaten",
        "type": WeaponType.MELEE,
    },
    "M24 STIELHANDGRANATE": {
        "name": "M24 Stielhandgranate",
        "type": WeaponType.GRENADE,
    },
    "M43 STIELHANDGRANATE": {
        "name": "M43 Stielhandgranate",
        "type": WeaponType.GRENADE,
    },
    "PANZERSCHRECK": {
        "name": "Panzerschreck",
        "type": WeaponType.ROCKET_LAUNCHER,
    },
    "S-MINE": {
        "name": "S-Mine",
        "type": WeaponType.AP_MINE,
    },
    "TELLERMINE 43": {
        "name": "Tellermine 43",
        "type": WeaponType.AT_MINE,
    },
    "75MM CANNON [PAK 40]": {
        "name": "75mm Cannon",
    },
    "150MM HOWITZER [sFH 18]": {
        "name": "150mm Howitzer",
    },
    "Sd.Kfz.234 Puma": {},
    "Sd.Kfz.121 Luchs": {},
    "Sd.Kfz.161 Panzer IV": {},
    "Sd.Kfz.171 Panther": {},
    "Sd.Kfz.181 Tiger 1": {},
    "Opel Blitz (Supply)": {},
    "Opel Blitz (Transport)": {},
    "Sd.Kfz 251 Half-track": {},
    "Kubelwagen": {},
    "Sturmpanzer IV": {},
    "Panzer III Ausf.N": {},
    "50mm KwK 39/1 [Sd.Kfz.234 Puma]": {
        "name": "50mm KwK 39/1",
    },
    "COAXIAL MG34 [Sd.Kfz.234 Puma]": {
        "name": "MG34",
    },
    "20MM KWK 30 [Sd.Kfz.121 Luchs]": {
        "name": "20mm KwK 30",
    },
    "COAXIAL MG34 [Sd.Kfz.121 Luchs]": {
        "name": "MG34",
    },
    "75MM CANNON [Sd.Kfz.161 Panzer IV]": {
        "name": "75mm Cannon",
    },
    "COAXIAL MG34 [Sd.Kfz.161 Panzer IV]": {
        "name": "MG34",
    },
    "HULL MG34 [Sd.Kfz.161 Panzer IV]": {
        "name": "MG34",
    },
    "75MM CANNON [Sd.Kfz.171 Panther]": {
        "name": "75mm Cannon",
    },
    "COAXIAL MG34 [Sd.Kfz.171 Panther]": {
        "name": "MG34",
    },
    "HULL MG34 [Sd.Kfz.171 Panther]": {
        "name": "MG34",
    },
    "88 KWK 36 L/56 [Sd.Kfz.181 Tiger 1]": {
        "name": "88mm KwK 36 L/56",
    },
    "COAXIAL MG34 [Sd.Kfz.181 Tiger 1]": {
        "name": "MG34",
    },
    "HULL MG34 [Sd.Kfz.181 Tiger 1]": {
        "name": "MG34",
    },
    "MG 42 [Sd.Kfz 251 Half-track]": {
        "name": "MG42",
        "type": WeaponType.MOUNTED_MG,
    },
    "StuH 43 L/12 [Sturmpanzer IV]": {
        "name": "StuH 43 L/12",
    },
    "7.5CM KwK 37 [Panzer III Ausf.N]": {
        "name": "75mm KwK 37",
    },
    "COAXIAL MG34 [Panzer III Ausf.N]": {
        "name": "MG34",
    },
    "HULL MG34 [Panzer III Ausf.N]": {
        "name": "MG34",
    },
    "150MM HOWITZER": {
        "name": "150mm Howitzer",
    },
    "50MM KWK 39/1": {
        "name": "50mm KwK 39/1",
    },
    "20MM KWK 30": {
        "name": "20mm KwK 30",
    },
    "88 KWK 36 L/56": {
        "name": "88mm KwK 36 L/56",
    },
    "COAXIAL MG34": {
        "name": "MG34",
    },
    "HULL MG34": {
        "name": "MG34",
    },
    "MG 42": {
        "name": "MG42",
        "type": WeaponType.MOUNTED_MG,
    },
    "7.5CM KwK 37": {
        "name": "75mm KwK 37",
    },
    "MOSIN NAGANT 1891": {
        "name": "Mosin-Nagant 1891",
        "type": WeaponType.BOLT_ACTION_RIFLE,
    },
    "MOSIN NAGANT 91/30": {
        "name": "Mosin-Nagant 91/30",
        "type": WeaponType.BOLT_ACTION_RIFLE,
    },
    "MOSIN NAGANT M38": {
        "name": "Mosin-Nagant M38",
        "type": WeaponType.BOLT_ACTION_RIFLE,
    },
    "SVT40": {
        "name": "SVT-40",
        "type": WeaponType.SEMI_AUTO_RIFLE,
    },
    "PPSH 41": {
        "name": "PPSh-41",
        "type": WeaponType.SUBMACHINE_GUN,
    },
    "PPSH 41 W/DRUM": {
        "name": "PPSh-41 with Drum",
        "type": WeaponType.SUBMACHINE_GUN,
    },
    "DP-27": {
        "name": "DP-27",
        "type": WeaponType.MACHINE_GUN,
    },
    "SCOPED MOSIN NAGANT 91/30": {
        "name": "Mosin-Nagant 91/30",
        "type": WeaponType.BOLT_ACTION_RIFLE,
        "magnification": 4,
    },
    "SCOPED SVT40": {
        "name": "SVT-40",
        "type": WeaponType.SEMI_AUTO_RIFLE,
        "magnification": 4,
    },
    "NAGANT M1895": {
        "name": "Nagant M1895",
        "type": WeaponType.REVOLVER,
    },
    "TOKAREV TT33": {
        "name": "Tokarev TT-33",
        "type": WeaponType.PISTOL,
    },
    "MPL-50 SPADE": {
        "name": "MPL-50 Spade",
        "type": WeaponType.MELEE,
    },
    "SATCHEL CHARGE": {
        "name": "Satchel Charge",
        "type": WeaponType.SATCHEL,
    },
    "RG-42 GRENADE": {
        "name": "RG-42 Grenade",
        "type": WeaponType.GRENADE,
    },
    "MOLOTOV": {
        "name": "Molotov",
        "type": WeaponType.GRENADE,
    },
    "PTRS-41": {
        "name": "PTRS-41",
        "type": WeaponType.ANTI_MATERIEL_RIFLE,
    },
    "POMZ AP MINE": {
        "name": "POMZ AP Mine",
        "type": WeaponType.AP_MINE,
    },
    "TM-35 AT MINE": {
        "name": "TM-35 AT Mine",
        "type": WeaponType.AT_MINE,
    },
    "57MM CANNON [ZiS-2]": {
        "name": "57mm Cannon",
    },
    "122MM HOWITZER [M1938 (M-30)]": {
        "name": "122mm Howitzer",
    },
    "BA-10": {},
    "T70": {},
    "T34/76": {},
    "IS-1": {},
    "ZIS-5 (Supply)": {},
    "ZIS-5 (Transport)": {},
    "KV-2": {},
    "GAZ-67": {},
    "19-K 45MM [BA-10]": {
        "name": "45mm M1932",
    },
    "COAXIAL DT [BA-10]": {
        "name": "DT",
    },
    "45MM M1937 [T70]": {
        "name": "45mm M1937",
    },
    "COAXIAL DT [T70]": {
        "name": "DT",
    },
    "76MM ZiS-5 [T34/76]": {
        "name": "76mm M1940",
    },
    "COAXIAL DT [T34/76]": {
        "name": "DT",
    },
    "HULL DT [T34/76]": {
        "name": "DT",
    },
    "D-5T 85MM [IS-1]": {
        "name": "D-5T 85mm",
    },
    "COAXIAL DT [IS-1]": {
        "name": "DT",
    },
    "HULL DT [IS-1]": {
        "name": "DT",
    },
    "152MM M-10T [KV-2]": {
        "name": "M-10T 152mm",
    },
    "HULL DT [KV-2]": {
        "name": "DT",
    },
    "122MM HOWITZER": {
        "name": "122mm Howitzer",
    },
    "19-K 45MM": {
        "name": "45mm M1932",
    },
    "45MM M1937": {
        "name": "45mm M1937",
    },
    "76MM ZiS-5": {
        "name": "76mm M1940",
    },
    "D-5T 85MM": {
        "name": "D-5T 85mm",
    },
    "COAXIAL DT": {
        "name": "COAXIAL DT",
    },
    "HULL DT": {
        "name": "HULL DT",
    },
    "152MM M-10T": {
        "name": "M-10T 152mm",
    },
    "SMLE No.1 Mk III": {
        "name": "SMLE Mk III",
        "type": WeaponType.BOLT_ACTION_RIFLE,
    },
    "Rifle No.4 Mk I": {
        "name": "No.4 Rifle Mk I",
        "type": WeaponType.BOLT_ACTION_RIFLE,
    },
    "Sten Gun Mk.II": {
        "name": "Sten Mk II",
        "type": WeaponType.SUBMACHINE_GUN,
    },
    "Sten Gun Mk.V": {
        "name": "Sten Mk V",
        "type": WeaponType.SUBMACHINE_GUN,
    },
    "M1928A1 THOMPSON": {
        "name": "M1928A1 Thompson",
        "type": WeaponType.SUBMACHINE_GUN,
    },
    "Bren Gun": {
        "name": "Bren Gun",
        "type": WeaponType.ASSAULT_RIFLE,
    },
    "Lewis Gun": {
        "name": "Lewis Gun",
        "type": WeaponType.MACHINE_GUN,
    },
    "FLAMETHROWER": {
        "name": "Lifebuoy Flamethrower",
        "type": WeaponType.FLAMETHROWER,
    },
    "Rifle No.4 Mk I Sniper": {
        "name": "No.4 Rifle Mk I",
        "type": WeaponType.BOLT_ACTION_RIFLE,
        "magnification": 8,
    },
    "Webley MK VI": {
        "name": "Webley Mk IV",
        "type": WeaponType.REVOLVER,
    },
    "Fairbairn–Sykes": {
        "name": "Fairbairn-Sykes",
        "type": WeaponType.MELEE,
    },
    "Satchel": {
        "name": "Satchel Charge",
        "type": WeaponType.SATCHEL,
    },
    "Mills Bomb": {
        "name": "Mills Bomb",
        "type": WeaponType.GRENADE,
    },
    "No.82 Grenade": {
        "name": "Gammon Bomb",
        "type": WeaponType.GRENADE,
    },
    "PIAT": {
        "name": "PIAT",
        "type": WeaponType.ROCKET_LAUNCHER,
    },
    "Boys Anti-tank Rifle": {
        "name": "Boys AT Rifle",
        "type": WeaponType.ANTI_MATERIEL_RIFLE,
    },
    "A.P. Shrapnel Mine Mk II": {
        "name": "AP Shrapnel Mine Mk II",
        "type": WeaponType.AP_MINE,
    },
    "A.T. Mine G.S. Mk V": {
        "name": "AT Mine G.S. Mk V",
        "type": WeaponType.AT_MINE,
    },
    "No.2 Mk 5 Flare Pistol": {
        "name": "No.2 Mk V Flare Gun",
        "type": WeaponType.RECON_FLARE,
    },
    "QF 6-POUNDER [QF 6-Pounder]": {
        "name": "57mm Cannon",
    },
    "QF 25-POUNDER [QF 25-Pounder]": {
        "name": "88mm Howitzer",
    },
    "Daimler": {},
    "Tetrarch": {},
    "M3 Stuart Honey": {},
    "Cromwell": {},
    "Crusader Mk.III": {},
    "Firefly": {},
    "Churchill Mk.III": {},
    "Churchill Mk.VII": {},
    "Bedford OYD (Supply)": {},
    "Bedford OYD (Transport)": {},
    "Churchill Mk III A.V.R.E.": {},
    "Bishop SP 25pdr": {},
    "QF 2-POUNDER [Daimler]": {
        "name": "QF 2-Pounder",
    },
    "COAXIAL BESA [Daimler]": {
        "name": "BESA",
    },
    "QF 2-POUNDER [Tetrarch]": {
        "name": "QF 2-Pounder",
    },
    "COAXIAL BESA [Tetrarch]": {
        "name": "BESA",
    },
    "37MM CANNON [M3 Stuart Honey]": {
        "name": "37mm Cannon",
    },
    "COAXIAL M1919 [M3 Stuart Honey]": {
        "name": "M1919 Browning",
    },
    "HULL M1919 [M3 Stuart Honey]": {
        "name": "M1919 Browning",
    },
    "OQF 75MM [Cromwell]": {
        "name": "QF 75mm",
    },
    "COAXIAL BESA [Cromwell]": {
        "name": "BESA",
    },
    "HULL BESA [Cromwell]": {
        "name": "BESA",
    },
    "OQF 57MM [Crusader Mk.III]": {
        "name": "QF 57mm",
    },
    "COAXIAL BESA [Crusader Mk.III]": {
        "name": "BESA",
    },
    "QF 17-POUNDER [Firefly]": {
        "name": "QF 17-Pounder",
    },
    "COAXIAL M1919 [Firefly]": {
        "name": "M1919 Browning",
    },
    "OQF 57MM [Churchill Mk.III]": {
        "name": "QF 57mm",
    },
    "COAXIAL BESA 7.92mm [Churchill Mk.III]": {
        "name": "BESA",
    },
    "HULL BESA 7.92mm [Churchill Mk.III]": {
        "name": "BESA",
    },
    "OQF 75MM [Churchill Mk.VII]": {
        "name": "QF 75mm",
    },
    "COAXIAL BESA 7.92mm [Churchill Mk.VII]": {
        "name": "BESA",
    },
    "HULL BESA 7.92mm [Churchill Mk.VII]": {
        "name": "BESA",
    },
    "230MM PETARD [Churchill Mk III A.V.R.E.]": {
        "name": "230mm Petard",
    },
    "COAXIAL BESA 7.92mm [Churchill Mk III A.V.R.E.]": {
        "name": "BESA",
    },
    "HULL BESA 7.92mm [Churchill Mk III A.V.R.E.]": {
        "name": "BESA",
    },
    "QF 25 POUNDER [Bishop SP 25pdr]": {
        "name": "88mm Howitzer",
    },
    "QF 6-POUNDER": {
        "name": "57mm Cannon",
    },
    "QF 25-POUNDER": {
        "name": "88mm Howitzer",
    },
    "QF 2-POUNDER": {
        "name": "QF 2-Pounder",
    },
    "OQF 75MM": {
        "name": "QF 75mm",
    },
    "OQF 57MM": {
        "name": "QF 57mm",
    },
    "QF 17-POUNDER": {
        "name": "QF 17-Pounder",
    },
    "COAXIAL BESA": {
        "name": "BESA",
    },
    "COAXIAL BESA 7.92mm": {
        "name": "BESA",
    },
    "HULL BESA": {
        "name": "BESA",
    },
    "HULL BESA 7.92mm": {
        "name": "7.92mm",
    },
    "QF 25 POUNDER": {
        "meth_name": "V_QF_25_POUNDER__UNKNOWN_2",
        "name": "88mm Howitzer",
    },
    "UNKNOWN": {
        "name": "Unknown",
    },
    "BOMBING RUN": {
        "name": "Bombing Run",
        "type": WeaponType.COMMANDER_ABILITY,
    },
    "STRAFING RUN": {
        "name": "Strafing Run",
        "type": WeaponType.COMMANDER_ABILITY,
    },
    "PRECISION STRIKE": {
        "name": "Precision Strike",
        "type": WeaponType.COMMANDER_ABILITY,
    },
    "Unknown": {
        "name": "Artillery Strike",
        "type": WeaponType.COMMANDER_ABILITY,
    },
    "FireSpot": {
        "name": "Fire",
    },
    "SMALL AMMUNITION BOX": {
        "name": "Small Ammunition Box",
        "type": WeaponType.SUPPLIES,
    },
    "HAMMER": {
        "name": "Hammer",
        "type": WeaponType.HAMMER,
    },
    "BANDAGE": {
        "name": "Bandage",
        "type": WeaponType.HEALING,
    },
    "NB39 NEBELHANDGRANATE": {
        "name": "NB39 Nebelhandgranate",
        "type": WeaponType.SMOKE_GRENADE,
    },
    "EXPLOSIVE AMMO BOX": {
        "name": "Explosive Ammo Box",
        "type": WeaponType.SUPPLIES,
    },
    "MORPHINE AMPOULE": {
        "name": "Morphine",
        "type": WeaponType.HEALING,
    },
    "MEDICAL SUPPLIES": {
        "name": "Medical Supplies",
        "type": WeaponType.SUPPLIES,
    },
    "WATCH": {
        "name": "Watch",
        "type": WeaponType.WATCH,
    },
    "DIENSTGLAS 6×30": {
        "name": "Dienstglas 6x30",
        "type": WeaponType.BINOCULARS,
    },
    "SUPPLIES": {
        "name": "Supplies",
        "type": WeaponType.SUPPLIES,
    },
    "PAK 40": {
        "name": "Wrench",
        "type": WeaponType.WRENCH,
    },
    "WRENCH": {
        "name": "Wrench",
        "type": WeaponType.WRENCH,
    },
    "TORCH": {
        "name": "Torch",
        "type": WeaponType.TORCH,
    },
    "EXTERIOR CUSTOMIZATION": {
        "name": "Exterior Customization",
        "type": WeaponType.WRENCH,
    },
    "M18 SMOKE GRENADE": {
        "name": "M18 Smoke Grenade",
        "type": WeaponType.SMOKE_GRENADE,
    },
    "MORPHINE SYRETTE": {
        "name": "Morphine Syrette",
        "type": WeaponType.HEALING,
    },
    "WESTINGHOUSE M3 6×30": {
        "name": "Westinghouse M3 6x30",
        "type": WeaponType.BINOCULARS,
    },
    "57MM M1": {
        "name": "Wrench",
        "type": WeaponType.WRENCH,
    },
    "RDG-2 SMOKE": {
        "name": "RDG-2 Smoke Grenade",
        "type": WeaponType.SMOKE_GRENADE,
    },
    "REVIVE": {
        "name": "Revive",
        "type": WeaponType.HEALING,
    },
    "RKKA 8×40": {
        "name": "RKKA 8x40",
        "type": WeaponType.BINOCULARS,
    },
    "ZiS-2": {
        "name": "ZiS-2",
        "type": WeaponType.WRENCH,
    },
    "Bandage": {
        "name": "Bandage",
        "type": WeaponType.HEALING,
    },
    "Hammer": {
        "name": "Hammer",
        "type": WeaponType.HAMMER,
    },
    "Small Ammunition Box": {
        "name": "Small Ammunition Box",
        "type": WeaponType.SUPPLIES,
    },
    "No.77": {
        "name": "No.77 WP Grenade",
        "type": WeaponType.SMOKE_GRENADE,
    },
    "Explosive Ammo Box": {
        "name": "Explosive Ammo Box",
        "type": WeaponType.SUPPLIES,
    },
    "Morphine": {
        "name": "Morphine",
        "type": WeaponType.HEALING,
    },
    "Medical Supplies": {
        "name": "Medical Supplies",
        "type": WeaponType.SUPPLIES,
    },
    "Watch": {
        "name": "Watch",
        "type": WeaponType.WATCH,
    },
    "Prism No.2 Mk II x6": {
        "name": "Prism No.2 Mk II x6",
        "type": WeaponType.BINOCULARS,
    },
    "Supplies": {
        "name": "Supplies",
        "type": WeaponType.SUPPLIES,
    },
    "Ordnance QF 6-pounder": {
        "name": "Ordnance QF 6-pounder",
        "type": WeaponType.WRENCH,
    },
    "Wrench": {
        "name": "Wrench",
        "type": WeaponType.WRENCH,
    },
    "Torch": {
        "name": "Torch",
        "type": WeaponType.TORCH,
    },
    "PRIMARY [BA-10]": {
        "name": "Receive Intel",
    },
    "PRIMARY [Daimler]": {
        "name": "Receive Intel",
    },
    "Exhaust Fuel Injection [IS-1]": {
        "name": "Smoke Screen",
    },
    "PRIMARY [M8 Greyhound]": {
        "name": "Receive Intel",
    },
    "PRIMARY [Sd.Kfz.234 Puma]": {
        "name": "Receive Intel",
    },
    "230MM PETARD": {
        "name": "230mm Petard",
    },
    "105MM HOWITZER": {
        "name": "105mm Howitzer",
    },
    "M6 37mm": {
        "name": "37mm Cannon",
    },
    "50mm KwK 39/1": {
        "name": "50mm KwK 39/1",
    },
    "StuH 43 L/12": {
        "name": "StuH 43 L/12",
    },
}

HLLV_WEAPON_METADATA: dict[str, WeaponMetaData] = {
    "M16A1": {
        "name": "M16A1",
        "type": WeaponType.ASSAULT_RIFLE,
    },
    "TNT": {
        "name": "TNT",
        "type": WeaponType.SATCHEL,
    },
    "Light Mortar": {
        "name": "Wrench",
        "type": WeaponType.WRENCH,
    },
    "M18 Claymore": {
        "name": "M18 Claymore",
        "type": WeaponType.AP_MINE,
    },
    "M1911A1": {
        "name": "M1911A1",
        "type": WeaponType.PISTOL,
    },
    "M16A1-M203": {
        "name": "M16A1 w/M203",
        "type": WeaponType.ASSAULT_RIFLE,
    },
    "M16A1 With Bayonet": {
        "name": "M16A1 w/Bayonet",
        "type": WeaponType.ASSAULT_RIFLE,
    },
    "M60": {
        "name": "M60",
        "type": WeaponType.MACHINE_GUN,
    },
    "M61 Frag Grenade": {
        "name": "M61 Grenade",
        "type": WeaponType.GRENADE,
    },
    "M183 Demolition Charge": {
        "name": "M183 Demolition Charge",
        "type": WeaponType.SATCHEL,
    },
    "Wrench": {
        "name": "Wrench",
        "type": WeaponType.WRENCH,
    },
    "M18 Smoke Grenade": {
        "name": "M18 Smoke Grenade",
        "type": WeaponType.SMOKE_GRENADE,
    },
    "M40": {
        "name": "M40",
        "type": WeaponType.BOLT_ACTION_RIFLE,
        "magnification": 4,  # TODO: Might be different magnification
    },
    "M79 ": {
        "name": "M79 Grenade Launcher",
        "type": WeaponType.GRENADE_LAUNCHER,
    },
    "M72 ": {
        "name": "M72 LAW",
        "type": WeaponType.ROCKET_LAUNCHER,
    },
    "M2A1-7": {
        "name": "M2 Flamethrower",
        "type": WeaponType.FLAMETHROWER,
    },
    "Model 77E": {
        "name": "Model 77E",
        "type": WeaponType.SHOTGUN,
    },
    "M3 Knife": {
        "name": "M3 Knife",
        "type": WeaponType.MELEE,
    },
    "M3 Binoculars": {
        "name": "M3 Binoculars",
        "type": WeaponType.BINOCULARS,
    },
    "FIELD PAD": {
        "name": "Field Pad",
        "type": WeaponType.WATCH,
    },
    "Supplies": {
        "name": "Supplies",
        "type": WeaponType.SUPPLIES,
    },
    "Hammer": {
        "name": "Hammer",
        "type": WeaponType.HAMMER,
    },
    "Medical Supplies": {
        "name": "Medical Supplies",
        "type": WeaponType.SUPPLIES,
    },
    "REVIVE": {
        "meth_name": "REVIVE_US",
        "type": WeaponType.HEALING,
        "name": "Revive",
    },
    "BANDAGE": {
        "meth_name": "BANDAGE_US",
        "type": WeaponType.HEALING,
        "name": "Bandage",
    },
    "Small Ammunition Box": {
        "name": "Small Ammo Box",
        "type": WeaponType.SUPPLIES,
    },
    "Explosive Ammo Box": {
        "name": "Explosive Ammo Box",
        "type": WeaponType.SUPPLIES,
    },
    "M21 AT Mine": {
        "name": "M21 AT Mine",
        "type": WeaponType.AT_MINE,
    },
    "BLOW TORCH": {
        "name": "Blowtorch",
        "type": WeaponType.TORCH,
    },
    "AN-M8 Flare": {
        "name": "AN-M8 Flare Pistol",
        "type": WeaponType.RECON_FLARE,
    },
    "RPG-02": {
        "name": "RPG-02",
        "type": WeaponType.ROCKET_LAUNCHER,
    },
    "TM-46 AT Mine": {
        "name": "TM-46 AT Mine",
        "type": WeaponType.AT_MINE,
    },
    "Type 53 PU": {
        "name": "Type 53",
        "type": WeaponType.BOLT_ACTION_RIFLE,
        "magnification": 4,  # TODO: Might be 3.5
    },
    "LPO-50": {
        "name": "LPO-50 Flamethrower",
        "type": WeaponType.FLAMETHROWER,
    },
    "IZH 58": {
        "name": "IZh-58",
        "type": WeaponType.SHOTGUN,
    },
    "Type 53 W/ N4 Rifle Launcher": {
        "name": "Type 53 w/N4",
        "type": WeaponType.BOLT_ACTION_RIFLE,
    },
    "RPD": {
        "name": "RPD",
        "type": WeaponType.MACHINE_GUN,
    },
    "K50M": {
        "name": "K-50M",
        "type": WeaponType.SUBMACHINE_GUN,
    },
    "K50M Drum": {
        "name": "K-50M w/Drum",
        "type": WeaponType.SUBMACHINE_GUN,
    },
    "Type 54": {
        "name": "Type 54",
        "type": WeaponType.PISTOL,
    },
    "DH10 AP Mine": {
        "name": "DH-10 AP Mine",
        "type": WeaponType.AP_MINE,
    },
    "Type 67": {
        "name": "Type 67 Grenade",
        "type": WeaponType.GRENADE,
    },
    "Knife": {
        "name": "Knife",
        "type": WeaponType.MELEE,
    },
    "Anti-Aircraft Gun Wrench": {
        "name": "Wrench",
        "type": WeaponType.WRENCH,
    },
    "RDG-1": {
        "name": "RDG-1 Smoke Grenade",
        "type": WeaponType.SMOKE_GRENADE,
    },
    "Binoculars": {
        "name": "Binoculars",
        "type": WeaponType.BINOCULARS,
    },
    "Type 56 W/ Bayonet": {
        "name": "Type 56 w/Bayonet",
        "type": WeaponType.ASSAULT_RIFLE,
    },
    "Ammo Box": {
        "name": "Small Ammo Box",
        "type": WeaponType.SUPPLIES,
    },
    "HE Ammo Box": {
        "name": "Explosive Ammo Box",
        "type": WeaponType.SUPPLIES,
    },
    "Revive": {
        "meth_name": "REVIVE_NVA",
        "type": WeaponType.HEALING,
        "name": "Revive",
    },
    "Bandage": {
        "meth_name": "BANDAGE_NVA",
        "type": WeaponType.HEALING,
        "name": "Bandage",
    },
    "Satchel Charge": {
        "name": "Satchel Charge",
        "type": WeaponType.SATCHEL,
    },
    "Type 53": {
        "name": "Type 53",
        "type": WeaponType.BOLT_ACTION_RIFLE,
    },
    "Chi Com Signal Pistol": {
        "name": "Chi-Com Flare Pistol",
        "type": WeaponType.RECON_FLARE,
    },
    "Dhsk [NVA Boat]": {
        "name": "DShK",
    },
    "RPD [NVA Boat]": {
        "name": "RPD",
    },
    "100MM D-10T CANNON [Sd.Kfz.171 Panther]": {
        "name": "100mm D-10T",
    },
    "SGMT 7.62MM [Sd.Kfz.171 Panther]": {
        "name": "SGMT",
    },
    "None [Sd.Kfz.171 Panther]": {
        "name": "Smoke Screen",
    },
    "M2 Browning [US Boat]": {
        "name": "M2 Browning",
    },
    "Flare Gun [US Transport Helicopter]": {
        "name": "Flare Gun",
    },
    "M60D [US Transport Helicopter]": {
        "name": "M60D",
    },
    "MORTAR [MORTAR]": {
        "name": "Mortar",
    },
    "DShKM Anti-Aircraft Gun [DShKM Anti-Aircraft Gun]": {
        "name": "DShK",
    },
    "Gaz 63 (Supply)": {},
    "Gaz 63 (Transport)": {},
    "M35 (Supply)": {},
    "M35 (Transport)": {},
    "NVA Boat": {},
    "Sd.Kfz.171 Panther": {},
    "100MM D-10T CANNON": {},
    "SGMT 7.62MM": {
        "name": "SGMT",
    },
    "US Boat": {},
    "US Supply Helicopter": {},
    "US Transport Helicopter": {},
    "MORTAR": {
        "name": "Mortar",
    },
    "DShKM Anti-Aircraft Gun": {
        "name": "DShK",
    },
}
