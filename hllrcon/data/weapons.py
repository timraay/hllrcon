# ruff: noqa: N802, D400, D415

from enum import StrEnum
from functools import cached_property
from typing import TYPE_CHECKING, Annotated, Generic, TypeAlias, TypeVar

from pydantic import Field

from hllrcon.data._utils import (
    IndexedBaseModel,
    class_cached_property,
    model_sequence_serializer,
)
from hllrcon.data.factions import HLLFaction, HLLVFaction, _Faction

if TYPE_CHECKING:
    from hllrcon.data.vehicles import HLLVehicle, HLLVVehicle, _Vehicle


FactionT = TypeVar("FactionT", bound=_Faction)
WeaponTypeT = TypeVar("WeaponTypeT", bound="_WeaponType")
VehicleT = TypeVar("VehicleT", bound="_Vehicle")


class _WeaponType(StrEnum):
    pass


class HLLWeaponType(_WeaponType):
    BOLT_ACTION_RIFLE = "Bolt Action Rifle"
    SEMI_AUTO_RIFLE = "Semi-Auto Rifle"
    ASSAULT_RIFLE = "Assault Rifle"
    SUBMACHINE_GUN = "Submachine Gun"
    MACHINE_GUN = "Machine Gun"
    SHOTGUN = "Shotgun"
    PISTOL = "Pistol"
    REVOLVER = "Revolver"
    GRENADE = "Grenade"
    AP_MINE = "Anti-Personnel Mine"
    AT_MINE = "Anti-Tank Mine"
    FLAMETHROWER = "Flamethrower"
    MELEE = "Melee"
    FLARE_GUN = "Flare Gun"
    ROCKET_LAUNCHER = "Rocket Launcher"
    ANTI_MATERIEL_RIFLE = "Anti-Materiel Rifle"
    AT_GUN = "Anti-Tank Gun"
    TANK_CANNON = "Tank Cannon"
    TANK_COAXIAL_MG = "Tank Coaxial MG"
    TANK_HULL_MG = "Tank Hull MG"
    MOUNTED_MG = "Mounted MG"
    ROADKILL = "Roadkill"
    ARTILLERY = "Artillery"
    COMMANDER_ABILITY = "Commander Ability"
    SATCHEL = "Satchel"
    NON_LETHAL = "Non-Lethal"
    UNKNOWN = "Unknown"


class HLLVWeaponType(_WeaponType):
    pass


WeaponType: TypeAlias = HLLWeaponType | HLLVWeaponType


class _Weapon(IndexedBaseModel[str], Generic[FactionT, WeaponTypeT, VehicleT]):
    id: str
    name: str
    type: WeaponTypeT
    vehicle_id: str | None = None
    factions: Annotated[
        set[FactionT],
        Field(min_length=1),
        model_sequence_serializer(int),
    ]
    magnification: int | None = None


class HLLWeapon(_Weapon[HLLFaction, HLLWeaponType, "HLLVehicle"]):
    # @computed_field(repr=False)
    @cached_property
    def vehicle(self) -> "HLLVehicle | None":
        from hllrcon.data.vehicles import HLLVehicle  # noqa: PLC0415

        if self.vehicle_id:
            return HLLVehicle.by_id(self.vehicle_id)
        return None

    # --- American weapons ---

    @class_cached_property
    @classmethod
    def M1_GARAND(cls) -> "HLLWeapon":
        """*M1 GARAND*"""
        return cls(
            id="M1 GARAND",
            name="M1 Garand",
            factions={HLLFaction.US},
            type=HLLWeaponType.SEMI_AUTO_RIFLE,
        )

    @class_cached_property
    @classmethod
    def M1_CARBINE(cls) -> "HLLWeapon":
        """*M1 CARBINE*"""
        return cls(
            id="M1 CARBINE",
            name="M1 Carbine",
            factions={HLLFaction.US},
            type=HLLWeaponType.SEMI_AUTO_RIFLE,
        )

    @class_cached_property
    @classmethod
    def M1A1_THOMPSON(cls) -> "HLLWeapon":
        """*M1A1 THOMPSON*"""
        return cls(
            id="M1A1 THOMPSON",
            name="M1A1 Thompson",
            factions={HLLFaction.US},
            type=HLLWeaponType.SUBMACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def M3_GREASE_GUN(cls) -> "HLLWeapon":
        """*M3 GREASE GUN*"""
        return cls(
            id="M3 GREASE GUN",
            name="M3 Grease Gun",
            factions={HLLFaction.US},
            type=HLLWeaponType.SUBMACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def M1918A2_BAR(cls) -> "HLLWeapon":
        """*M1918A2 BAR*"""
        return cls(
            id="M1918A2 BAR",
            name="M1918A2 BAR",
            factions={HLLFaction.US},
            type=HLLWeaponType.ASSAULT_RIFLE,
        )

    @class_cached_property
    @classmethod
    def BROWNING_M1919(cls) -> "HLLWeapon":
        """*BROWNING M1919*"""
        return cls(
            id="BROWNING M1919",
            name="M1919 Browning",
            factions={HLLFaction.US},
            type=HLLWeaponType.MACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def M1903_SPRINGFIELD_SCOPED_4X(cls) -> "HLLWeapon":
        """*M1903 SPRINGFIELD*"""
        return cls(
            id="M1903 SPRINGFIELD",
            name="M1903 Springfield",
            factions={HLLFaction.US},
            type=HLLWeaponType.BOLT_ACTION_RIFLE,
            magnification=4,
        )

    @class_cached_property
    @classmethod
    def M97_TRENCH_GUN(cls) -> "HLLWeapon":
        """*M97 TRENCH GUN*"""
        return cls(
            id="M97 TRENCH GUN",
            name="M97 Trench Gun",
            factions={HLLFaction.US},
            type=HLLWeaponType.SHOTGUN,
        )

    @class_cached_property
    @classmethod
    def COLT_M1911(cls) -> "HLLWeapon":
        """*COLT M1911*"""
        return cls(
            id="COLT M1911",
            name="Colt M1911",
            factions={HLLFaction.US},
            type=HLLWeaponType.PISTOL,
        )

    @class_cached_property
    @classmethod
    def M3_KNIFE(cls) -> "HLLWeapon":
        """*M3 KNIFE*"""
        return cls(
            id="M3 KNIFE",
            name="M3 Knife",
            factions={HLLFaction.US},
            type=HLLWeaponType.MELEE,
        )

    @class_cached_property
    @classmethod
    def SATCHEL_CHARGE(cls) -> "HLLWeapon":
        """*SATCHEL*"""
        return cls(
            id="SATCHEL",
            name="Satchel Charge",
            factions={HLLFaction.US, HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.SATCHEL,
        )

    @class_cached_property
    @classmethod
    def MK2_GRENADE(cls) -> "HLLWeapon":
        """*MK2 GRENADE*"""
        return cls(
            id="MK2 GRENADE",
            name="Mk 2 Grenade",
            factions={HLLFaction.US},
            type=HLLWeaponType.GRENADE,
        )

    @class_cached_property
    @classmethod
    def M2_FLAMETHROWER(cls) -> "HLLWeapon":
        """*M2 FLAMETHROWER*"""
        return cls(
            id="M2 FLAMETHROWER",
            name="M2 Flamethrower",
            factions={HLLFaction.US},
            type=HLLWeaponType.FLAMETHROWER,
        )

    @class_cached_property
    @classmethod
    def BAZOOKA(cls) -> "HLLWeapon":
        """*BAZOOKA*"""
        return cls(
            id="BAZOOKA",
            name="Bazooka",
            factions={HLLFaction.US},
            type=HLLWeaponType.ROCKET_LAUNCHER,
        )

    @class_cached_property
    @classmethod
    def M2_AP_MINE(cls) -> "HLLWeapon":
        """*M2 AP MINE*"""
        return cls(
            id="M2 AP MINE",
            name="M2 AP Mine",
            factions={HLLFaction.US},
            type=HLLWeaponType.AP_MINE,
        )

    @class_cached_property
    @classmethod
    def M1A1_AT_MINE(cls) -> "HLLWeapon":
        """*M1A1 AT MINE*"""
        return cls(
            id="M1A1 AT MINE",
            name="M1A1 AT Mine",
            factions={HLLFaction.US},
            type=HLLWeaponType.AT_MINE,
        )

    @class_cached_property
    @classmethod
    def FLARE_GUN(cls) -> "HLLWeapon":
        """*FLARE GUN*"""
        return cls(
            id="FLARE GUN",
            name="Flare Gun",
            factions={HLLFaction.US, HLLFaction.GER, HLLFaction.DAK, HLLFaction.SOV},
            type=HLLWeaponType.FLARE_GUN,
        )

    # --- German weapons ---

    @class_cached_property
    @classmethod
    def KARABINER_98K(cls) -> "HLLWeapon":
        """*KARABINER 98K*"""
        return cls(
            id="KARABINER 98K",
            name="Karabiner 98k",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.BOLT_ACTION_RIFLE,
        )

    @class_cached_property
    @classmethod
    def GEWEHR_43(cls) -> "HLLWeapon":
        """*GEWEHR 43*"""
        return cls(
            id="GEWEHR 43",
            name="G43",
            factions={HLLFaction.GER},
            type=HLLWeaponType.SEMI_AUTO_RIFLE,
        )

    @class_cached_property
    @classmethod
    def STG44(cls) -> "HLLWeapon":
        """*STG44*"""
        return cls(
            id="STG44",
            name="STG44",
            factions={HLLFaction.GER},
            type=HLLWeaponType.ASSAULT_RIFLE,
        )

    @class_cached_property
    @classmethod
    def FG42(cls) -> "HLLWeapon":
        """*FG42*"""
        return cls(
            id="FG42",
            name="FG42",
            factions={HLLFaction.GER},
            type=HLLWeaponType.ASSAULT_RIFLE,
        )

    @class_cached_property
    @classmethod
    def MP40(cls) -> "HLLWeapon":
        """*MP40*"""
        return cls(
            id="MP40",
            name="MP40",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.SUBMACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def MG34(cls) -> "HLLWeapon":
        """*MG34*"""
        return cls(
            id="MG34",
            name="MG34",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.MACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def MG42(cls) -> "HLLWeapon":
        """*MG42*"""
        return cls(
            id="MG42",
            name="MG42",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.MACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def FLAMMENWERFER_41(cls) -> "HLLWeapon":
        """*FLAMMENWERFER 41*"""
        return cls(
            id="FLAMMENWERFER 41",
            name="Flammenwerfer 41",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.FLAMETHROWER,
        )

    @class_cached_property
    @classmethod
    def KARABINER_98K_SCOPED_8X(cls) -> "HLLWeapon":
        """*KARABINER 98K x8*"""
        return cls(
            id="KARABINER 98K x8",
            name="Karabiner 98k",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.BOLT_ACTION_RIFLE,
            magnification=8,
        )

    @class_cached_property
    @classmethod
    def FG42_SCOPED_4X(cls) -> "HLLWeapon":
        """*FG42 x4*"""
        return cls(
            id="FG42 x4",
            name="FG42",
            factions={HLLFaction.GER},
            type=HLLWeaponType.SEMI_AUTO_RIFLE,
            magnification=4,
        )

    @class_cached_property
    @classmethod
    def LUGER_P08(cls) -> "HLLWeapon":
        """*LUGER P08*"""
        return cls(
            id="LUGER P08",
            name="Luger P08",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.PISTOL,
        )

    @class_cached_property
    @classmethod
    def WALTHER_P38(cls) -> "HLLWeapon":
        """*WALTHER P38*"""
        return cls(
            id="WALTHER P38",
            name="Walther P38",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.PISTOL,
        )

    @class_cached_property
    @classmethod
    def FELDSPATEN(cls) -> "HLLWeapon":
        """*FELDSPATEN*"""
        return cls(
            id="FELDSPATEN",
            name="Feldspaten",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.MELEE,
        )

    # SATCHEL

    @class_cached_property
    @classmethod
    def M24_STIELHANDGRANATE(cls) -> "HLLWeapon":
        """*M24 STIELHANDGRANATE*"""
        return cls(
            id="M24 STIELHANDGRANATE",
            name="M24 Stielhandgranate",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.GRENADE,
        )

    @class_cached_property
    @classmethod
    def M43_STIELHANDGRANATE(cls) -> "HLLWeapon":
        """*M43 STIELHANDGRANATE*"""
        return cls(
            id="M43 STIELHANDGRANATE",
            name="M43 Stielhandgranate",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.GRENADE,
        )

    @class_cached_property
    @classmethod
    def PANZERSCHRECK(cls) -> "HLLWeapon":
        """*PANZERSCHRECK*"""
        return cls(
            id="PANZERSCHRECK",
            name="Panzerschreck",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.ROCKET_LAUNCHER,
        )

    @class_cached_property
    @classmethod
    def S_MINE(cls) -> "HLLWeapon":
        """*S-MINE*"""
        return cls(
            id="S-MINE",
            name="S-Mine",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.AP_MINE,
        )

    @class_cached_property
    @classmethod
    def TELLERMINE_43(cls) -> "HLLWeapon":
        """*TELLERMINE 43*"""
        return cls(
            id="TELLERMINE 43",
            name="Tellermine 43",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.AT_MINE,
        )

    # FLARE GUN

    # --- Soviet weapons ---

    @class_cached_property
    @classmethod
    def MOSIN_NAGANT_1891(cls) -> "HLLWeapon":
        """*MOSIN NAGANT 1891*"""
        return cls(
            id="MOSIN NAGANT 1891",
            name="Mosin-Nagant 1891",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.BOLT_ACTION_RIFLE,
        )

    @class_cached_property
    @classmethod
    def MOSIN_NAGANT_91_30(cls) -> "HLLWeapon":
        """*MOSIN NAGANT 91/30*"""
        return cls(
            id="MOSIN NAGANT 91/30",
            name="Mosin-Nagant 91/30",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.BOLT_ACTION_RIFLE,
        )

    @class_cached_property
    @classmethod
    def MOSIN_NAGANT_M38(cls) -> "HLLWeapon":
        """*MOSIN NAGANT M38*"""
        return cls(
            id="MOSIN NAGANT M38",
            name="Mosin-Nagant M38",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.BOLT_ACTION_RIFLE,
        )

    @class_cached_property
    @classmethod
    def SVT_40(cls) -> "HLLWeapon":
        """*SVT40*"""
        return cls(
            id="SVT40",
            name="SVT-40",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.SEMI_AUTO_RIFLE,
        )

    @class_cached_property
    @classmethod
    def PPSH_41(cls) -> "HLLWeapon":
        """*PPSH 41*"""
        return cls(
            id="PPSH 41",
            name="PPSh-41",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.SUBMACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def PPSH_41_WITH_DRUM(cls) -> "HLLWeapon":
        """*PPSH 41 W/DRUM*"""
        return cls(
            id="PPSH 41 W/DRUM",
            name="PPSh-41 with Drum",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.SUBMACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def DP_27(cls) -> "HLLWeapon":
        """*DP-27*"""
        return cls(
            id="DP-27",
            name="DP-27",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.MACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def MOSIN_NAGANT_91_30_SCOPED_4X(cls) -> "HLLWeapon":
        """*SCOPED MOSIN NAGANT 91/30*"""
        return cls(
            id="SCOPED MOSIN NAGANT 91/30",
            name="Mosin-Nagant 91/30",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.BOLT_ACTION_RIFLE,
            magnification=4,
        )

    @class_cached_property
    @classmethod
    def SVT_40_SCOPED_4X(cls) -> "HLLWeapon":
        """*SCOPED SVT40*"""
        return cls(
            id="SCOPED SVT40",
            name="SVT-40",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.SEMI_AUTO_RIFLE,
            magnification=4,
        )

    @class_cached_property
    @classmethod
    def NAGANT_M1895(cls) -> "HLLWeapon":
        """*NAGANT M1895*"""
        return cls(
            id="NAGANT M1895",
            name="Nagant M1895",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.REVOLVER,
        )

    @class_cached_property
    @classmethod
    def TOKAREV_TT33(cls) -> "HLLWeapon":
        """*TOKAREV TT33*"""
        return cls(
            id="TOKAREV TT33",
            name="Tokarev TT-33",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.PISTOL,
        )

    @class_cached_property
    @classmethod
    def MPL_50_SPADE(cls) -> "HLLWeapon":
        """*MPL-50 SPADE*"""
        return cls(
            id="MPL-50 SPADE",
            name="MPL-50 Spade",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.MELEE,
        )

    @class_cached_property
    @classmethod
    def SATCHEL_CHARGE_SOVIET(cls) -> "HLLWeapon":
        """*SATCHEL CHARGE*"""
        return cls(
            id="SATCHEL CHARGE",
            name="Satchel Charge",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.SATCHEL,
        )

    @class_cached_property
    @classmethod
    def RG_42_GRENADE(cls) -> "HLLWeapon":
        """*RG-42 GRENADE*"""
        return cls(
            id="RG-42 GRENADE",
            name="RG-42 Grenade",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.GRENADE,
        )

    @class_cached_property
    @classmethod
    def MOLOTOV(cls) -> "HLLWeapon":
        """*MOLOTOV*"""
        return cls(
            id="MOLOTOV",
            name="Molotov",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.GRENADE,
        )

    @class_cached_property
    @classmethod
    def PTRS_41(cls) -> "HLLWeapon":
        """*PTRS-41*"""
        return cls(
            id="PTRS-41",
            name="PTRS-41",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.ANTI_MATERIEL_RIFLE,
        )

    @class_cached_property
    @classmethod
    def POMZ_AP_MINE(cls) -> "HLLWeapon":
        """*POMZ AP MINE*"""
        return cls(
            id="POMZ AP MINE",
            name="POMZ AP Mine",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.AP_MINE,
        )

    @class_cached_property
    @classmethod
    def TM_35_AT_MINE(cls) -> "HLLWeapon":
        """*TM-35 AT MINE*"""
        return cls(
            id="TM-35 AT MINE",
            name="TM-35 AT Mine",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.AT_MINE,
        )

    # FLARE GUN

    # --- British weapons ---

    @class_cached_property
    @classmethod
    def SMLE_NO_1_MK_III(cls) -> "HLLWeapon":
        """*SMLE No.1 Mk III*"""
        return cls(
            id="SMLE No.1 Mk III",
            name="SMLE Mk III",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.BOLT_ACTION_RIFLE,
        )

    @class_cached_property
    @classmethod
    def RIFLE_NO_4_MK_I(cls) -> "HLLWeapon":
        """*Rifle No.4 Mk I*"""
        return cls(
            id="Rifle No.4 Mk I",
            name="No.4 Rifle Mk I",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.BOLT_ACTION_RIFLE,
        )

    @class_cached_property
    @classmethod
    def STEN_GUN_MK_II(cls) -> "HLLWeapon":
        """*Sten Gun Mk.II*"""
        return cls(
            id="Sten Gun Mk.II",
            name="Sten Mk II",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.SUBMACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def STEN_GUN(cls) -> "HLLWeapon":
        """*Sten Gun Mk.II*"""
        return cls.STEN_GUN_MK_II

    @class_cached_property
    @classmethod
    def STEN_GUN_MK_V(cls) -> "HLLWeapon":
        """*Sten Gun Mk.V*"""
        return cls(
            id="Sten Gun Mk.V",
            name="Sten Mk V",
            factions={HLLFaction.CW},
            type=HLLWeaponType.SUBMACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def M1928A1_THOMPSON(cls) -> "HLLWeapon":
        """*M1928A1 THOMPSON*"""
        return cls(
            id="M1928A1 THOMPSON",
            name="M1928A1 Thompson",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.SUBMACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def BREN_GUN(cls) -> "HLLWeapon":
        """*Bren Gun*"""
        return cls(
            id="Bren Gun",
            name="Bren Gun",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.ASSAULT_RIFLE,
        )

    @class_cached_property
    @classmethod
    def LEWIS_GUN(cls) -> "HLLWeapon":
        """*Lewis Gun*"""
        return cls(
            id="Lewis Gun",
            name="Lewis Gun",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.MACHINE_GUN,
        )

    @class_cached_property
    @classmethod
    def LIFEBUOY_FLAMETHROWER(cls) -> "HLLWeapon":
        """*FLAMETHROWER*"""
        return cls(
            id="FLAMETHROWER",
            name="Lifebuoy Flamethrower",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.FLAMETHROWER,
        )

    @class_cached_property
    @classmethod
    def RIFLE_NO_4_MK_I_SCOPED_8X(cls) -> "HLLWeapon":
        """*Rifle No.4 Mk I Sniper*"""
        return cls(
            id="Rifle No.4 Mk I Sniper",
            name="No.4 Rifle Mk I",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.BOLT_ACTION_RIFLE,
            magnification=8,
        )

    @class_cached_property
    @classmethod
    def WEBLEY_MK_VI(cls) -> "HLLWeapon":
        """*Webley MK VI*"""
        return cls(
            id="Webley MK VI",
            name="Webley Mk IV",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.REVOLVER,
        )

    @class_cached_property
    @classmethod
    def FAIRBAIRN_SYKES(cls) -> "HLLWeapon":
        """*Fairbairn–Sykes*"""  # noqa: RUF002
        return cls(
            id="Fairbairn–Sykes",  # noqa: RUF001
            name="Fairbairn-Sykes",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.MELEE,
        )

    @class_cached_property
    @classmethod
    def SATCHEL_CHARGE_COMMONWEALTH(cls) -> "HLLWeapon":
        """*Satchel*"""
        return cls(
            id="Satchel",
            name="Satchel Charge",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.SATCHEL,
        )

    @class_cached_property
    @classmethod
    def MILLS_BOMB(cls) -> "HLLWeapon":
        """*Mills Bomb*"""
        return cls(
            id="Mills Bomb",
            name="Mills Bomb",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.GRENADE,
        )

    @class_cached_property
    @classmethod
    def GAMMON_BOMB(cls) -> "HLLWeapon":
        """*No.82 Grenade*"""
        return cls(
            id="No.82 Grenade",
            name="Gammon Bomb",
            factions={HLLFaction.CW},
            type=HLLWeaponType.GRENADE,
        )

    @class_cached_property
    @classmethod
    def PIAT(cls) -> "HLLWeapon":
        """*PIAT*"""
        return cls(
            id="PIAT",
            name="PIAT",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.ROCKET_LAUNCHER,
        )

    @class_cached_property
    @classmethod
    def BOYS_ANTI_TANK_RIFLE(cls) -> "HLLWeapon":
        """*Boys Anti-tank Rifle*"""
        return cls(
            id="Boys Anti-tank Rifle",
            name="Boys AT Rifle",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.ANTI_MATERIEL_RIFLE,
        )

    @class_cached_property
    @classmethod
    def AP_SHRAPNEL_MINE_MK_II(cls) -> "HLLWeapon":
        """*A.P. Shrapnel Mine Mk II*"""
        return cls(
            id="A.P. Shrapnel Mine Mk II",
            name="AP Shrapnel Mine Mk II",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.AP_MINE,
        )

    @class_cached_property
    @classmethod
    def AT_MINE_GS_MK_V(cls) -> "HLLWeapon":
        """*A.T. Mine G.S. Mk V*"""
        return cls(
            id="A.T. Mine G.S. Mk V",
            name="AT Mine G.S. Mk V",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.AT_MINE,
        )

    @class_cached_property
    @classmethod
    def NO_2_MK_V_FLARE_GUN(cls) -> "HLLWeapon":
        """*No.2 Mk 5 Flare Pistol*"""
        return cls(
            id="No.2 Mk 5 Flare Pistol",
            name="No.2 Mk V Flare Gun",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.FLARE_GUN,
        )

    ### INJECT "hll vehicles" START

    @class_cached_property
    @classmethod
    def V_105MM_HOWITZER__UNKNOWN(cls) -> "HLLWeapon":
        """*105MM HOWITZER*"""
        return cls(
            id="105MM HOWITZER",
            name="105MM HOWITZER",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_105MM_HOWITZER__M4A3_105MM(cls) -> "HLLWeapon":
        """*105MM HOWITZER [M4A3 (105mm)]*"""
        return cls(
            id="105MM HOWITZER [M4A3 (105mm)]",
            name="105MM HOWITZER",
            vehicle_id="M4A3 (105mm)",
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_152MM_M_10T__UNKNOWN(cls) -> "HLLWeapon":
        """*152MM M-10T*"""
        return cls(
            id="152MM M-10T",
            name="152MM M-10T",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_152MM_M_10T__KV_2(cls) -> "HLLWeapon":
        """*152MM M-10T [KV-2]*"""
        return cls(
            id="152MM M-10T [KV-2]",
            name="152MM M-10T",
            vehicle_id="KV-2",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_19_K_45MM__UNKNOWN(cls) -> "HLLWeapon":
        """*19-K 45MM*"""
        return cls(
            id="19-K 45MM",
            name="19-K 45MM",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_19_K_45MM__BA_10(cls) -> "HLLWeapon":
        """*19-K 45MM [BA-10]*"""
        return cls(
            id="19-K 45MM [BA-10]",
            name="19-K 45MM",
            vehicle_id="BA-10",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_20MM_KWK_30__UNKNOWN(cls) -> "HLLWeapon":
        """*20MM KWK 30*"""
        return cls(
            id="20MM KWK 30",
            name="20MM KWK 30",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_20MM_KWK_30__SDKFZ121_LUCHS(cls) -> "HLLWeapon":
        """*20MM KWK 30 [Sd.Kfz.121 Luchs]*"""
        return cls(
            id="20MM KWK 30 [Sd.Kfz.121 Luchs]",
            name="20MM KWK 30",
            vehicle_id="Sd.Kfz.121 Luchs",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_230MM_PETARD__UNKNOWN(cls) -> "HLLWeapon":
        """*230MM PETARD*"""
        return cls(
            id="230MM PETARD",
            name="230MM PETARD",
            vehicle_id=None,
            factions={HLLFaction.CW},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_230MM_PETARD__CHURCHILL_MK_III_AVRE(cls) -> "HLLWeapon":
        """*230MM PETARD [Churchill Mk III A.V.R.E.]*"""
        return cls(
            id="230MM PETARD [Churchill Mk III A.V.R.E.]",
            name="230MM PETARD",
            vehicle_id="Churchill Mk III A.V.R.E.",
            factions={HLLFaction.CW},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_37MM_CANNON__UNKNOWN(cls) -> "HLLWeapon":
        """*37MM CANNON*"""
        return cls(
            id="37MM CANNON",
            name="37MM CANNON",
            vehicle_id=None,
            factions={HLLFaction.US, HLLFaction.B8A},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_37MM_CANNON__M3_STUART_HONEY(cls) -> "HLLWeapon":
        """*37MM CANNON [M3 Stuart Honey]*"""
        return cls(
            id="37MM CANNON [M3 Stuart Honey]",
            name="37MM CANNON",
            vehicle_id="M3 Stuart Honey",
            factions={HLLFaction.B8A},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_37MM_CANNON__STUART_M5A1(cls) -> "HLLWeapon":
        """*37MM CANNON [Stuart M5A1]*"""
        return cls(
            id="37MM CANNON [Stuart M5A1]",
            name="37MM CANNON",
            vehicle_id="Stuart M5A1",
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_45MM_M1937__UNKNOWN(cls) -> "HLLWeapon":
        """*45MM M1937*"""
        return cls(
            id="45MM M1937",
            name="45MM M1937",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_45MM_M1937__T70(cls) -> "HLLWeapon":
        """*45MM M1937 [T70]*"""
        return cls(
            id="45MM M1937 [T70]",
            name="45MM M1937",
            vehicle_id="T70",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_50MM_KWK_39_1__UNKNOWN(cls) -> "HLLWeapon":
        """*50mm KwK 39/1*"""
        return cls(
            id="50mm KwK 39/1",
            name="50mm KwK 39/1",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_50MM_KWK_39_1__SDKFZ234_PUMA(cls) -> "HLLWeapon":
        """*50mm KwK 39/1 [Sd.Kfz.234 Puma]*"""
        return cls(
            id="50mm KwK 39/1 [Sd.Kfz.234 Puma]",
            name="50mm KwK 39/1",
            vehicle_id="Sd.Kfz.234 Puma",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_75CM_KWK_37__UNKNOWN(cls) -> "HLLWeapon":
        """*7.5CM KwK 37*"""
        return cls(
            id="7.5CM KwK 37",
            name="7.5CM KwK 37",
            vehicle_id=None,
            factions={HLLFaction.DAK},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_75CM_KWK_37__PANZER_III_AUSFN(cls) -> "HLLWeapon":
        """*7.5CM KwK 37 [Panzer III Ausf.N]*"""
        return cls(
            id="7.5CM KwK 37 [Panzer III Ausf.N]",
            name="7.5CM KwK 37",
            vehicle_id="Panzer III Ausf.N",
            factions={HLLFaction.DAK},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_75MM_CANNON__UNKNOWN(cls) -> "HLLWeapon":
        """*75MM CANNON*"""
        return cls(
            id="75MM CANNON",
            name="75MM CANNON",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.US, HLLFaction.DAK},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_75MM_CANNON__SDKFZ161_PANZER_IV(cls) -> "HLLWeapon":
        """*75MM CANNON [Sd.Kfz.161 Panzer IV]*"""
        return cls(
            id="75MM CANNON [Sd.Kfz.161 Panzer IV]",
            name="75MM CANNON",
            vehicle_id="Sd.Kfz.161 Panzer IV",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_75MM_CANNON__SDKFZ171_PANTHER(cls) -> "HLLWeapon":
        """*75MM CANNON [Sd.Kfz.171 Panther]*"""
        return cls(
            id="75MM CANNON [Sd.Kfz.171 Panther]",
            name="75MM CANNON",
            vehicle_id="Sd.Kfz.171 Panther",
            factions={HLLFaction.GER},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_75MM_CANNON__SHERMAN_M4A375W(cls) -> "HLLWeapon":
        """*75MM CANNON [Sherman M4A3(75)W]*"""
        return cls(
            id="75MM CANNON [Sherman M4A3(75)W]",
            name="75MM CANNON",
            vehicle_id="Sherman M4A3(75)W",
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_75MM_M3_GUN__UNKNOWN(cls) -> "HLLWeapon":
        """*75MM M3 GUN*"""
        return cls(
            id="75MM M3 GUN",
            name="75MM M3 GUN",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_75MM_M3_GUN__SHERMAN_M4A3E2(cls) -> "HLLWeapon":
        """*75MM M3 GUN [Sherman M4A3E2]*"""
        return cls(
            id="75MM M3 GUN [Sherman M4A3E2]",
            name="75MM M3 GUN",
            vehicle_id="Sherman M4A3E2",
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_76MM_M1_GUN__UNKNOWN(cls) -> "HLLWeapon":
        """*76MM M1 GUN*"""
        return cls(
            id="76MM M1 GUN",
            name="76MM M1 GUN",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_76MM_M1_GUN__SHERMAN_M4A3E276(cls) -> "HLLWeapon":
        """*76MM M1 GUN [Sherman M4A3E2(76)]*"""
        return cls(
            id="76MM M1 GUN [Sherman M4A3E2(76)]",
            name="76MM M1 GUN",
            vehicle_id="Sherman M4A3E2(76)",
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_76MM_ZIS_5__UNKNOWN(cls) -> "HLLWeapon":
        """*76MM ZiS-5*"""
        return cls(
            id="76MM ZiS-5",
            name="76MM ZiS-5",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_76MM_ZIS_5__T34_76(cls) -> "HLLWeapon":
        """*76MM ZiS-5 [T34/76]*"""
        return cls(
            id="76MM ZiS-5 [T34/76]",
            name="76MM ZiS-5",
            vehicle_id="T34/76",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_88_KWK_36_L_56__UNKNOWN(cls) -> "HLLWeapon":
        """*88 KWK 36 L/56*"""
        return cls(
            id="88 KWK 36 L/56",
            name="88 KWK 36 L/56",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_88_KWK_36_L_56__SDKFZ181_TIGER_1(cls) -> "HLLWeapon":
        """*88 KWK 36 L/56 [Sd.Kfz.181 Tiger 1]*"""
        return cls(
            id="88 KWK 36 L/56 [Sd.Kfz.181 Tiger 1]",
            name="88 KWK 36 L/56",
            vehicle_id="Sd.Kfz.181 Tiger 1",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__BA_10(cls) -> "HLLWeapon":
        """*BA-10*"""
        return cls(
            id="BA-10",
            name="BA-10",
            vehicle_id="BA-10",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__BEDFORD_OYD_SUPPLY(cls) -> "HLLWeapon":
        """*Bedford OYD (Supply)*"""
        return cls(
            id="Bedford OYD (Supply)",
            name="Bedford OYD (Supply)",
            vehicle_id="Bedford OYD (Supply)",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__BEDFORD_OYD_TRANSPORT(cls) -> "HLLWeapon":
        """*Bedford OYD (Transport)*"""
        return cls(
            id="Bedford OYD (Transport)",
            name="Bedford OYD (Transport)",
            vehicle_id="Bedford OYD (Transport)",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__BISHOP_SP_25PDR(cls) -> "HLLWeapon":
        """*Bishop SP 25pdr*"""
        return cls(
            id="Bishop SP 25pdr",
            name="Bishop SP 25pdr",
            vehicle_id="Bishop SP 25pdr",
            factions={HLLFaction.B8A},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA__UNKNOWN(cls) -> "HLLWeapon":
        """*COAXIAL BESA*"""
        return cls(
            id="COAXIAL BESA",
            name="COAXIAL BESA",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA_792MM__UNKNOWN(cls) -> "HLLWeapon":
        """*COAXIAL BESA 7.92mm*"""
        return cls(
            id="COAXIAL BESA 7.92mm",
            name="COAXIAL BESA 7.92mm",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA_792MM__CHURCHILL_MK_III_AVRE(cls) -> "HLLWeapon":
        """*COAXIAL BESA 7.92mm [Churchill Mk III A.V.R.E.]*"""
        return cls(
            id="COAXIAL BESA 7.92mm [Churchill Mk III A.V.R.E.]",
            name="COAXIAL BESA 7.92mm",
            vehicle_id="Churchill Mk III A.V.R.E.",
            factions={HLLFaction.CW},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA_792MM__CHURCHILL_MKIII(cls) -> "HLLWeapon":
        """*COAXIAL BESA 7.92mm [Churchill Mk.III]*"""
        return cls(
            id="COAXIAL BESA 7.92mm [Churchill Mk.III]",
            name="COAXIAL BESA 7.92mm",
            vehicle_id="Churchill Mk.III",
            factions={HLLFaction.B8A},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA_792MM__CHURCHILL_MKVII(cls) -> "HLLWeapon":
        """*COAXIAL BESA 7.92mm [Churchill Mk.VII]*"""
        return cls(
            id="COAXIAL BESA 7.92mm [Churchill Mk.VII]",
            name="COAXIAL BESA 7.92mm",
            vehicle_id="Churchill Mk.VII",
            factions={HLLFaction.CW},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA__CROMWELL(cls) -> "HLLWeapon":
        """*COAXIAL BESA [Cromwell]*"""
        return cls(
            id="COAXIAL BESA [Cromwell]",
            name="COAXIAL BESA",
            vehicle_id="Cromwell",
            factions={HLLFaction.CW},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA__CRUSADER_MKIII(cls) -> "HLLWeapon":
        """*COAXIAL BESA [Crusader Mk.III]*"""
        return cls(
            id="COAXIAL BESA [Crusader Mk.III]",
            name="COAXIAL BESA",
            vehicle_id="Crusader Mk.III",
            factions={HLLFaction.B8A},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA__DAIMLER(cls) -> "HLLWeapon":
        """*COAXIAL BESA [Daimler]*"""
        return cls(
            id="COAXIAL BESA [Daimler]",
            name="COAXIAL BESA",
            vehicle_id="Daimler",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA__TETRARCH(cls) -> "HLLWeapon":
        """*COAXIAL BESA [Tetrarch]*"""
        return cls(
            id="COAXIAL BESA [Tetrarch]",
            name="COAXIAL BESA",
            vehicle_id="Tetrarch",
            factions={HLLFaction.CW},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_DT__UNKNOWN(cls) -> "HLLWeapon":
        """*COAXIAL DT*"""
        return cls(
            id="COAXIAL DT",
            name="COAXIAL DT",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_DT__BA_10(cls) -> "HLLWeapon":
        """*COAXIAL DT [BA-10]*"""
        return cls(
            id="COAXIAL DT [BA-10]",
            name="COAXIAL DT",
            vehicle_id="BA-10",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_DT__IS_1(cls) -> "HLLWeapon":
        """*COAXIAL DT [IS-1]*"""
        return cls(
            id="COAXIAL DT [IS-1]",
            name="COAXIAL DT",
            vehicle_id="IS-1",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_DT__T34_76(cls) -> "HLLWeapon":
        """*COAXIAL DT [T34/76]*"""
        return cls(
            id="COAXIAL DT [T34/76]",
            name="COAXIAL DT",
            vehicle_id="T34/76",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_DT__T70(cls) -> "HLLWeapon":
        """*COAXIAL DT [T70]*"""
        return cls(
            id="COAXIAL DT [T70]",
            name="COAXIAL DT",
            vehicle_id="T70",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__UNKNOWN(cls) -> "HLLWeapon":
        """*COAXIAL M1919*"""
        return cls(
            id="COAXIAL M1919",
            name="COAXIAL M1919",
            vehicle_id=None,
            factions={HLLFaction.US, HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__FIREFLY(cls) -> "HLLWeapon":
        """*COAXIAL M1919 [Firefly]*"""
        return cls(
            id="COAXIAL M1919 [Firefly]",
            name="COAXIAL M1919",
            vehicle_id="Firefly",
            factions={HLLFaction.CW},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__M3_STUART_HONEY(cls) -> "HLLWeapon":
        """*COAXIAL M1919 [M3 Stuart Honey]*"""
        return cls(
            id="COAXIAL M1919 [M3 Stuart Honey]",
            name="COAXIAL M1919",
            vehicle_id="M3 Stuart Honey",
            factions={HLLFaction.B8A},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__M4A3_105MM(cls) -> "HLLWeapon":
        """*COAXIAL M1919 [M4A3 (105mm)]*"""
        return cls(
            id="COAXIAL M1919 [M4A3 (105mm)]",
            name="COAXIAL M1919",
            vehicle_id="M4A3 (105mm)",
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__M8_GREYHOUND(cls) -> "HLLWeapon":
        """*COAXIAL M1919 [M8 Greyhound]*"""
        return cls(
            id="COAXIAL M1919 [M8 Greyhound]",
            name="COAXIAL M1919",
            vehicle_id="M8 Greyhound",
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__SHERMAN_M4A375W(cls) -> "HLLWeapon":
        """*COAXIAL M1919 [Sherman M4A3(75)W]*"""
        return cls(
            id="COAXIAL M1919 [Sherman M4A3(75)W]",
            name="COAXIAL M1919",
            vehicle_id="Sherman M4A3(75)W",
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__SHERMAN_M4A3E276(cls) -> "HLLWeapon":
        """*COAXIAL M1919 [Sherman M4A3E2(76)]*"""
        return cls(
            id="COAXIAL M1919 [Sherman M4A3E2(76)]",
            name="COAXIAL M1919",
            vehicle_id="Sherman M4A3E2(76)",
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__SHERMAN_M4A3E2(cls) -> "HLLWeapon":
        """*COAXIAL M1919 [Sherman M4A3E2]*"""
        return cls(
            id="COAXIAL M1919 [Sherman M4A3E2]",
            name="COAXIAL M1919",
            vehicle_id="Sherman M4A3E2",
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__STUART_M5A1(cls) -> "HLLWeapon":
        """*COAXIAL M1919 [Stuart M5A1]*"""
        return cls(
            id="COAXIAL M1919 [Stuart M5A1]",
            name="COAXIAL M1919",
            vehicle_id="Stuart M5A1",
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__UNKNOWN(cls) -> "HLLWeapon":
        """*COAXIAL MG34*"""
        return cls(
            id="COAXIAL MG34",
            name="COAXIAL MG34",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__PANZER_III_AUSFN(cls) -> "HLLWeapon":
        """*COAXIAL MG34 [Panzer III Ausf.N]*"""
        return cls(
            id="COAXIAL MG34 [Panzer III Ausf.N]",
            name="COAXIAL MG34",
            vehicle_id="Panzer III Ausf.N",
            factions={HLLFaction.DAK},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__SDKFZ121_LUCHS(cls) -> "HLLWeapon":
        """*COAXIAL MG34 [Sd.Kfz.121 Luchs]*"""
        return cls(
            id="COAXIAL MG34 [Sd.Kfz.121 Luchs]",
            name="COAXIAL MG34",
            vehicle_id="Sd.Kfz.121 Luchs",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__SDKFZ161_PANZER_IV(cls) -> "HLLWeapon":
        """*COAXIAL MG34 [Sd.Kfz.161 Panzer IV]*"""
        return cls(
            id="COAXIAL MG34 [Sd.Kfz.161 Panzer IV]",
            name="COAXIAL MG34",
            vehicle_id="Sd.Kfz.161 Panzer IV",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__SDKFZ171_PANTHER(cls) -> "HLLWeapon":
        """*COAXIAL MG34 [Sd.Kfz.171 Panther]*"""
        return cls(
            id="COAXIAL MG34 [Sd.Kfz.171 Panther]",
            name="COAXIAL MG34",
            vehicle_id="Sd.Kfz.171 Panther",
            factions={HLLFaction.GER},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__SDKFZ181_TIGER_1(cls) -> "HLLWeapon":
        """*COAXIAL MG34 [Sd.Kfz.181 Tiger 1]*"""
        return cls(
            id="COAXIAL MG34 [Sd.Kfz.181 Tiger 1]",
            name="COAXIAL MG34",
            vehicle_id="Sd.Kfz.181 Tiger 1",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__SDKFZ234_PUMA(cls) -> "HLLWeapon":
        """*COAXIAL MG34 [Sd.Kfz.234 Puma]*"""
        return cls(
            id="COAXIAL MG34 [Sd.Kfz.234 Puma]",
            name="COAXIAL MG34",
            vehicle_id="Sd.Kfz.234 Puma",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.TANK_COAXIAL_MG,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__CHURCHILL_MK_III_AVRE(cls) -> "HLLWeapon":
        """*Churchill Mk III A.V.R.E.*"""
        return cls(
            id="Churchill Mk III A.V.R.E.",
            name="Churchill Mk III A.V.R.E.",
            vehicle_id="Churchill Mk III A.V.R.E.",
            factions={HLLFaction.CW},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__CHURCHILL_MKIII(cls) -> "HLLWeapon":
        """*Churchill Mk.III*"""
        return cls(
            id="Churchill Mk.III",
            name="Churchill Mk.III",
            vehicle_id="Churchill Mk.III",
            factions={HLLFaction.B8A},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__CHURCHILL_MKVII(cls) -> "HLLWeapon":
        """*Churchill Mk.VII*"""
        return cls(
            id="Churchill Mk.VII",
            name="Churchill Mk.VII",
            vehicle_id="Churchill Mk.VII",
            factions={HLLFaction.CW},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__CROMWELL(cls) -> "HLLWeapon":
        """*Cromwell*"""
        return cls(
            id="Cromwell",
            name="Cromwell",
            vehicle_id="Cromwell",
            factions={HLLFaction.CW},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__CRUSADER_MKIII(cls) -> "HLLWeapon":
        """*Crusader Mk.III*"""
        return cls(
            id="Crusader Mk.III",
            name="Crusader Mk.III",
            vehicle_id="Crusader Mk.III",
            factions={HLLFaction.B8A},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_D_5T_85MM__UNKNOWN(cls) -> "HLLWeapon":
        """*D-5T 85MM*"""
        return cls(
            id="D-5T 85MM",
            name="D-5T 85MM",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_D_5T_85MM__IS_1(cls) -> "HLLWeapon":
        """*D-5T 85MM [IS-1]*"""
        return cls(
            id="D-5T 85MM [IS-1]",
            name="D-5T 85MM",
            vehicle_id="IS-1",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__DAIMLER(cls) -> "HLLWeapon":
        """*Daimler*"""
        return cls(
            id="Daimler",
            name="Daimler",
            vehicle_id="Daimler",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_EXHAUST_FUEL_INJECTION__UNKNOWN(cls) -> "HLLWeapon":
        """*Exhaust Fuel Injection*"""
        return cls(
            id="Exhaust Fuel Injection",
            name="Exhaust Fuel Injection",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=HLLWeaponType.NON_LETHAL,
        )

    @class_cached_property
    @classmethod
    def V_EXHAUST_FUEL_INJECTION__IS_1(cls) -> "HLLWeapon":
        """*Exhaust Fuel Injection [IS-1]*"""
        return cls(
            id="Exhaust Fuel Injection [IS-1]",
            name="Exhaust Fuel Injection",
            vehicle_id="IS-1",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.NON_LETHAL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__FIREFLY(cls) -> "HLLWeapon":
        """*Firefly*"""
        return cls(
            id="Firefly",
            name="Firefly",
            vehicle_id="Firefly",
            factions={HLLFaction.CW},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__GAZ_67(cls) -> "HLLWeapon":
        """*GAZ-67*"""
        return cls(
            id="GAZ-67",
            name="GAZ-67",
            vehicle_id="GAZ-67",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__GMC_CCKW_353_SUPPLY(cls) -> "HLLWeapon":
        """*GMC CCKW 353 (Supply)*"""
        return cls(
            id="GMC CCKW 353 (Supply)",
            name="GMC CCKW 353 (Supply)",
            vehicle_id="GMC CCKW 353 (Supply)",
            factions={HLLFaction.US},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__GMC_CCKW_353_TRANSPORT(cls) -> "HLLWeapon":
        """*GMC CCKW 353 (Transport)*"""
        return cls(
            id="GMC CCKW 353 (Transport)",
            name="GMC CCKW 353 (Transport)",
            vehicle_id="GMC CCKW 353 (Transport)",
            factions={HLLFaction.US},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_HULL_BESA__UNKNOWN(cls) -> "HLLWeapon":
        """*HULL BESA*"""
        return cls(
            id="HULL BESA",
            name="HULL BESA",
            vehicle_id=None,
            factions={HLLFaction.CW},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_BESA_792MM__UNKNOWN(cls) -> "HLLWeapon":
        """*HULL BESA 7.92mm*"""
        return cls(
            id="HULL BESA 7.92mm",
            name="HULL BESA 7.92mm",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_BESA_792MM__CHURCHILL_MK_III_AVRE(cls) -> "HLLWeapon":
        """*HULL BESA 7.92mm [Churchill Mk III A.V.R.E.]*"""
        return cls(
            id="HULL BESA 7.92mm [Churchill Mk III A.V.R.E.]",
            name="HULL BESA 7.92mm",
            vehicle_id="Churchill Mk III A.V.R.E.",
            factions={HLLFaction.CW},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_BESA_792MM__CHURCHILL_MKIII(cls) -> "HLLWeapon":
        """*HULL BESA 7.92mm [Churchill Mk.III]*"""
        return cls(
            id="HULL BESA 7.92mm [Churchill Mk.III]",
            name="HULL BESA 7.92mm",
            vehicle_id="Churchill Mk.III",
            factions={HLLFaction.B8A},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_BESA_792MM__CHURCHILL_MKVII(cls) -> "HLLWeapon":
        """*HULL BESA 7.92mm [Churchill Mk.VII]*"""
        return cls(
            id="HULL BESA 7.92mm [Churchill Mk.VII]",
            name="HULL BESA 7.92mm",
            vehicle_id="Churchill Mk.VII",
            factions={HLLFaction.CW},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_BESA__CROMWELL(cls) -> "HLLWeapon":
        """*HULL BESA [Cromwell]*"""
        return cls(
            id="HULL BESA [Cromwell]",
            name="HULL BESA",
            vehicle_id="Cromwell",
            factions={HLLFaction.CW},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_DT__UNKNOWN(cls) -> "HLLWeapon":
        """*HULL DT*"""
        return cls(
            id="HULL DT",
            name="HULL DT",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_DT__IS_1(cls) -> "HLLWeapon":
        """*HULL DT [IS-1]*"""
        return cls(
            id="HULL DT [IS-1]",
            name="HULL DT",
            vehicle_id="IS-1",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_DT__KV_2(cls) -> "HLLWeapon":
        """*HULL DT [KV-2]*"""
        return cls(
            id="HULL DT [KV-2]",
            name="HULL DT",
            vehicle_id="KV-2",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_DT__T34_76(cls) -> "HLLWeapon":
        """*HULL DT [T34/76]*"""
        return cls(
            id="HULL DT [T34/76]",
            name="HULL DT",
            vehicle_id="T34/76",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__UNKNOWN(cls) -> "HLLWeapon":
        """*HULL M1919*"""
        return cls(
            id="HULL M1919",
            name="HULL M1919",
            vehicle_id=None,
            factions={HLLFaction.US, HLLFaction.B8A},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__M3_STUART_HONEY(cls) -> "HLLWeapon":
        """*HULL M1919 [M3 Stuart Honey]*"""
        return cls(
            id="HULL M1919 [M3 Stuart Honey]",
            name="HULL M1919",
            vehicle_id="M3 Stuart Honey",
            factions={HLLFaction.B8A},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__M4A3_105MM(cls) -> "HLLWeapon":
        """*HULL M1919 [M4A3 (105mm)]*"""
        return cls(
            id="HULL M1919 [M4A3 (105mm)]",
            name="HULL M1919",
            vehicle_id="M4A3 (105mm)",
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__SHERMAN_M4A375W(cls) -> "HLLWeapon":
        """*HULL M1919 [Sherman M4A3(75)W]*"""
        return cls(
            id="HULL M1919 [Sherman M4A3(75)W]",
            name="HULL M1919",
            vehicle_id="Sherman M4A3(75)W",
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__SHERMAN_M4A3E276(cls) -> "HLLWeapon":
        """*HULL M1919 [Sherman M4A3E2(76)]*"""
        return cls(
            id="HULL M1919 [Sherman M4A3E2(76)]",
            name="HULL M1919",
            vehicle_id="Sherman M4A3E2(76)",
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__SHERMAN_M4A3E2(cls) -> "HLLWeapon":
        """*HULL M1919 [Sherman M4A3E2]*"""
        return cls(
            id="HULL M1919 [Sherman M4A3E2]",
            name="HULL M1919",
            vehicle_id="Sherman M4A3E2",
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__STUART_M5A1(cls) -> "HLLWeapon":
        """*HULL M1919 [Stuart M5A1]*"""
        return cls(
            id="HULL M1919 [Stuart M5A1]",
            name="HULL M1919",
            vehicle_id="Stuart M5A1",
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_MG34__UNKNOWN(cls) -> "HLLWeapon":
        """*HULL MG34*"""
        return cls(
            id="HULL MG34",
            name="HULL MG34",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_MG34__PANZER_III_AUSFN(cls) -> "HLLWeapon":
        """*HULL MG34 [Panzer III Ausf.N]*"""
        return cls(
            id="HULL MG34 [Panzer III Ausf.N]",
            name="HULL MG34",
            vehicle_id="Panzer III Ausf.N",
            factions={HLLFaction.DAK},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_MG34__SDKFZ161_PANZER_IV(cls) -> "HLLWeapon":
        """*HULL MG34 [Sd.Kfz.161 Panzer IV]*"""
        return cls(
            id="HULL MG34 [Sd.Kfz.161 Panzer IV]",
            name="HULL MG34",
            vehicle_id="Sd.Kfz.161 Panzer IV",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_MG34__SDKFZ171_PANTHER(cls) -> "HLLWeapon":
        """*HULL MG34 [Sd.Kfz.171 Panther]*"""
        return cls(
            id="HULL MG34 [Sd.Kfz.171 Panther]",
            name="HULL MG34",
            vehicle_id="Sd.Kfz.171 Panther",
            factions={HLLFaction.GER},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_HULL_MG34__SDKFZ181_TIGER_1(cls) -> "HLLWeapon":
        """*HULL MG34 [Sd.Kfz.181 Tiger 1]*"""
        return cls(
            id="HULL MG34 [Sd.Kfz.181 Tiger 1]",
            name="HULL MG34",
            vehicle_id="Sd.Kfz.181 Tiger 1",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.TANK_HULL_MG,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__IS_1(cls) -> "HLLWeapon":
        """*IS-1*"""
        return cls(
            id="IS-1",
            name="IS-1",
            vehicle_id="IS-1",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__JEEP_WILLYS(cls) -> "HLLWeapon":
        """*Jeep Willys*"""
        return cls(
            id="Jeep Willys",
            name="Jeep Willys",
            vehicle_id="Jeep Willys",
            factions={HLLFaction.US, HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__KV_2(cls) -> "HLLWeapon":
        """*KV-2*"""
        return cls(
            id="KV-2",
            name="KV-2",
            vehicle_id="KV-2",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__KUBELWAGEN(cls) -> "HLLWeapon":
        """*Kubelwagen*"""
        return cls(
            id="Kubelwagen",
            name="Kubelwagen",
            vehicle_id="Kubelwagen",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_M2_BROWNING__UNKNOWN(cls) -> "HLLWeapon":
        """*M2 Browning*"""
        return cls(
            id="M2 Browning",
            name="M2 Browning",
            vehicle_id=None,
            factions={HLLFaction.US, HLLFaction.SOV, HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.MOUNTED_MG,
        )

    @class_cached_property
    @classmethod
    def V_M2_BROWNING__M3_HALF_TRACK(cls) -> "HLLWeapon":
        """*M2 Browning [M3 Half-track]*"""
        return cls(
            id="M2 Browning [M3 Half-track]",
            name="M2 Browning",
            vehicle_id="M3 Half-track",
            factions={HLLFaction.US, HLLFaction.SOV, HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.MOUNTED_MG,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__M3_HALF_TRACK(cls) -> "HLLWeapon":
        """*M3 Half-track*"""
        return cls(
            id="M3 Half-track",
            name="M3 Half-track",
            vehicle_id="M3 Half-track",
            factions={HLLFaction.US, HLLFaction.SOV, HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__M3_STUART_HONEY(cls) -> "HLLWeapon":
        """*M3 Stuart Honey*"""
        return cls(
            id="M3 Stuart Honey",
            name="M3 Stuart Honey",
            vehicle_id="M3 Stuart Honey",
            factions={HLLFaction.B8A},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__M4A3_105MM(cls) -> "HLLWeapon":
        """*M4A3 (105mm)*"""
        return cls(
            id="M4A3 (105mm)",
            name="M4A3 (105mm)",
            vehicle_id="M4A3 (105mm)",
            factions={HLLFaction.US},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_M6_37MM__UNKNOWN(cls) -> "HLLWeapon":
        """*M6 37mm*"""
        return cls(
            id="M6 37mm",
            name="M6 37mm",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_M6_37MM__M8_GREYHOUND(cls) -> "HLLWeapon":
        """*M6 37mm [M8 Greyhound]*"""
        return cls(
            id="M6 37mm [M8 Greyhound]",
            name="M6 37mm",
            vehicle_id="M8 Greyhound",
            factions={HLLFaction.US},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__M8_GREYHOUND(cls) -> "HLLWeapon":
        """*M8 Greyhound*"""
        return cls(
            id="M8 Greyhound",
            name="M8 Greyhound",
            vehicle_id="M8 Greyhound",
            factions={HLLFaction.US},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_MG_42__UNKNOWN(cls) -> "HLLWeapon":
        """*MG 42*"""
        return cls(
            id="MG 42",
            name="MG 42",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.MOUNTED_MG,
        )

    @class_cached_property
    @classmethod
    def V_MG_42__SDKFZ_251_HALF_TRACK(cls) -> "HLLWeapon":
        """*MG 42 [Sd.Kfz 251 Half-track]*"""
        return cls(
            id="MG 42 [Sd.Kfz 251 Half-track]",
            name="MG 42",
            vehicle_id="Sd.Kfz 251 Half-track",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.MOUNTED_MG,
        )

    @class_cached_property
    @classmethod
    def V_OQF_57MM__UNKNOWN(cls) -> "HLLWeapon":
        """*OQF 57MM*"""
        return cls(
            id="OQF 57MM",
            name="OQF 57MM",
            vehicle_id=None,
            factions={HLLFaction.B8A},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_OQF_57MM__CHURCHILL_MKIII(cls) -> "HLLWeapon":
        """*OQF 57MM [Churchill Mk.III]*"""
        return cls(
            id="OQF 57MM [Churchill Mk.III]",
            name="OQF 57MM",
            vehicle_id="Churchill Mk.III",
            factions={HLLFaction.B8A},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_OQF_57MM__CRUSADER_MKIII(cls) -> "HLLWeapon":
        """*OQF 57MM [Crusader Mk.III]*"""
        return cls(
            id="OQF 57MM [Crusader Mk.III]",
            name="OQF 57MM",
            vehicle_id="Crusader Mk.III",
            factions={HLLFaction.B8A},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_OQF_75MM__UNKNOWN(cls) -> "HLLWeapon":
        """*OQF 75MM*"""
        return cls(
            id="OQF 75MM",
            name="OQF 75MM",
            vehicle_id=None,
            factions={HLLFaction.CW},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_OQF_75MM__CHURCHILL_MKVII(cls) -> "HLLWeapon":
        """*OQF 75MM [Churchill Mk.VII]*"""
        return cls(
            id="OQF 75MM [Churchill Mk.VII]",
            name="OQF 75MM",
            vehicle_id="Churchill Mk.VII",
            factions={HLLFaction.CW},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_OQF_75MM__CROMWELL(cls) -> "HLLWeapon":
        """*OQF 75MM [Cromwell]*"""
        return cls(
            id="OQF 75MM [Cromwell]",
            name="OQF 75MM",
            vehicle_id="Cromwell",
            factions={HLLFaction.CW},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__OPEL_BLITZ_SUPPLY(cls) -> "HLLWeapon":
        """*Opel Blitz (Supply)*"""
        return cls(
            id="Opel Blitz (Supply)",
            name="Opel Blitz (Supply)",
            vehicle_id="Opel Blitz (Supply)",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__OPEL_BLITZ_TRANSPORT(cls) -> "HLLWeapon":
        """*Opel Blitz (Transport)*"""
        return cls(
            id="Opel Blitz (Transport)",
            name="Opel Blitz (Transport)",
            vehicle_id="Opel Blitz (Transport)",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_PRIMARY__UNKNOWN(cls) -> "HLLWeapon":
        """*PRIMARY*"""
        return cls(
            id="PRIMARY",
            name="PRIMARY",
            vehicle_id=None,
            factions={
                HLLFaction.GER,
                HLLFaction.US,
                HLLFaction.SOV,
                HLLFaction.CW,
                HLLFaction.DAK,
                HLLFaction.B8A,
            },
            type=HLLWeaponType.NON_LETHAL,
        )

    @class_cached_property
    @classmethod
    def V_PRIMARY__BA_10(cls) -> "HLLWeapon":
        """*PRIMARY [BA-10]*"""
        return cls(
            id="PRIMARY [BA-10]",
            name="PRIMARY",
            vehicle_id="BA-10",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.NON_LETHAL,
        )

    @class_cached_property
    @classmethod
    def V_PRIMARY__DAIMLER(cls) -> "HLLWeapon":
        """*PRIMARY [Daimler]*"""
        return cls(
            id="PRIMARY [Daimler]",
            name="PRIMARY",
            vehicle_id="Daimler",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.NON_LETHAL,
        )

    @class_cached_property
    @classmethod
    def V_PRIMARY__M8_GREYHOUND(cls) -> "HLLWeapon":
        """*PRIMARY [M8 Greyhound]*"""
        return cls(
            id="PRIMARY [M8 Greyhound]",
            name="PRIMARY",
            vehicle_id="M8 Greyhound",
            factions={HLLFaction.US},
            type=HLLWeaponType.NON_LETHAL,
        )

    @class_cached_property
    @classmethod
    def V_PRIMARY__SDKFZ234_PUMA(cls) -> "HLLWeapon":
        """*PRIMARY [Sd.Kfz.234 Puma]*"""
        return cls(
            id="PRIMARY [Sd.Kfz.234 Puma]",
            name="PRIMARY",
            vehicle_id="Sd.Kfz.234 Puma",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.NON_LETHAL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__PANZER_III_AUSFN(cls) -> "HLLWeapon":
        """*Panzer III Ausf.N*"""
        return cls(
            id="Panzer III Ausf.N",
            name="Panzer III Ausf.N",
            vehicle_id="Panzer III Ausf.N",
            factions={HLLFaction.DAK},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_QF_17_POUNDER__UNKNOWN(cls) -> "HLLWeapon":
        """*QF 17-POUNDER*"""
        return cls(
            id="QF 17-POUNDER",
            name="QF 17-POUNDER",
            vehicle_id=None,
            factions={HLLFaction.CW},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_QF_17_POUNDER__FIREFLY(cls) -> "HLLWeapon":
        """*QF 17-POUNDER [Firefly]*"""
        return cls(
            id="QF 17-POUNDER [Firefly]",
            name="QF 17-POUNDER",
            vehicle_id="Firefly",
            factions={HLLFaction.CW},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_QF_2_POUNDER__UNKNOWN(cls) -> "HLLWeapon":
        """*QF 2-POUNDER*"""
        return cls(
            id="QF 2-POUNDER",
            name="QF 2-POUNDER",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_QF_2_POUNDER__DAIMLER(cls) -> "HLLWeapon":
        """*QF 2-POUNDER [Daimler]*"""
        return cls(
            id="QF 2-POUNDER [Daimler]",
            name="QF 2-POUNDER",
            vehicle_id="Daimler",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_QF_2_POUNDER__TETRARCH(cls) -> "HLLWeapon":
        """*QF 2-POUNDER [Tetrarch]*"""
        return cls(
            id="QF 2-POUNDER [Tetrarch]",
            name="QF 2-POUNDER",
            vehicle_id="Tetrarch",
            factions={HLLFaction.CW},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_QF_25_POUNDER__UNKNOWN(cls) -> "HLLWeapon":
        """*QF 25 POUNDER*"""
        return cls(
            id="QF 25 POUNDER",
            name="QF 25 POUNDER",
            vehicle_id=None,
            factions={HLLFaction.B8A},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_QF_25_POUNDER__BISHOP_SP_25PDR(cls) -> "HLLWeapon":
        """*QF 25 POUNDER [Bishop SP 25pdr]*"""
        return cls(
            id="QF 25 POUNDER [Bishop SP 25pdr]",
            name="QF 25 POUNDER",
            vehicle_id="Bishop SP 25pdr",
            factions={HLLFaction.B8A},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SDKFZ_251_HALF_TRACK(cls) -> "HLLWeapon":
        """*Sd.Kfz 251 Half-track*"""
        return cls(
            id="Sd.Kfz 251 Half-track",
            name="Sd.Kfz 251 Half-track",
            vehicle_id="Sd.Kfz 251 Half-track",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SDKFZ121_LUCHS(cls) -> "HLLWeapon":
        """*Sd.Kfz.121 Luchs*"""
        return cls(
            id="Sd.Kfz.121 Luchs",
            name="Sd.Kfz.121 Luchs",
            vehicle_id="Sd.Kfz.121 Luchs",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SDKFZ161_PANZER_IV(cls) -> "HLLWeapon":
        """*Sd.Kfz.161 Panzer IV*"""
        return cls(
            id="Sd.Kfz.161 Panzer IV",
            name="Sd.Kfz.161 Panzer IV",
            vehicle_id="Sd.Kfz.161 Panzer IV",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SDKFZ171_PANTHER(cls) -> "HLLWeapon":
        """*Sd.Kfz.171 Panther*"""
        return cls(
            id="Sd.Kfz.171 Panther",
            name="Sd.Kfz.171 Panther",
            vehicle_id="Sd.Kfz.171 Panther",
            factions={HLLFaction.GER},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SDKFZ181_TIGER_1(cls) -> "HLLWeapon":
        """*Sd.Kfz.181 Tiger 1*"""
        return cls(
            id="Sd.Kfz.181 Tiger 1",
            name="Sd.Kfz.181 Tiger 1",
            vehicle_id="Sd.Kfz.181 Tiger 1",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SDKFZ234_PUMA(cls) -> "HLLWeapon":
        """*Sd.Kfz.234 Puma*"""
        return cls(
            id="Sd.Kfz.234 Puma",
            name="Sd.Kfz.234 Puma",
            vehicle_id="Sd.Kfz.234 Puma",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SHERMAN_M4A375W(cls) -> "HLLWeapon":
        """*Sherman M4A3(75)W*"""
        return cls(
            id="Sherman M4A3(75)W",
            name="Sherman M4A3(75)W",
            vehicle_id="Sherman M4A3(75)W",
            factions={HLLFaction.US},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SHERMAN_M4A3E2(cls) -> "HLLWeapon":
        """*Sherman M4A3E2*"""
        return cls(
            id="Sherman M4A3E2",
            name="Sherman M4A3E2",
            vehicle_id="Sherman M4A3E2",
            factions={HLLFaction.US},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SHERMAN_M4A3E276(cls) -> "HLLWeapon":
        """*Sherman M4A3E2(76)*"""
        return cls(
            id="Sherman M4A3E2(76)",
            name="Sherman M4A3E2(76)",
            vehicle_id="Sherman M4A3E2(76)",
            factions={HLLFaction.US},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_STUH_43_L_12__UNKNOWN(cls) -> "HLLWeapon":
        """*StuH 43 L/12*"""
        return cls(
            id="StuH 43 L/12",
            name="StuH 43 L/12",
            vehicle_id=None,
            factions={HLLFaction.GER},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_STUH_43_L_12__STURMPANZER_IV(cls) -> "HLLWeapon":
        """*StuH 43 L/12 [Sturmpanzer IV]*"""
        return cls(
            id="StuH 43 L/12 [Sturmpanzer IV]",
            name="StuH 43 L/12",
            vehicle_id="Sturmpanzer IV",
            factions={HLLFaction.GER},
            type=HLLWeaponType.TANK_CANNON,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__STUART_M5A1(cls) -> "HLLWeapon":
        """*Stuart M5A1*"""
        return cls(
            id="Stuart M5A1",
            name="Stuart M5A1",
            vehicle_id="Stuart M5A1",
            factions={HLLFaction.US},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__STURMPANZER_IV(cls) -> "HLLWeapon":
        """*Sturmpanzer IV*"""
        return cls(
            id="Sturmpanzer IV",
            name="Sturmpanzer IV",
            vehicle_id="Sturmpanzer IV",
            factions={HLLFaction.GER},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__T34_76(cls) -> "HLLWeapon":
        """*T34/76*"""
        return cls(
            id="T34/76",
            name="T34/76",
            vehicle_id="T34/76",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__T70(cls) -> "HLLWeapon":
        """*T70*"""
        return cls(
            id="T70",
            name="T70",
            vehicle_id="T70",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__TETRARCH(cls) -> "HLLWeapon":
        """*Tetrarch*"""
        return cls(
            id="Tetrarch",
            name="Tetrarch",
            vehicle_id="Tetrarch",
            factions={HLLFaction.CW},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__ZIS_5_SUPPLY(cls) -> "HLLWeapon":
        """*ZIS-5 (Supply)*"""
        return cls(
            id="ZIS-5 (Supply)",
            name="ZIS-5 (Supply)",
            vehicle_id="ZIS-5 (Supply)",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.ROADKILL,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__ZIS_5_TRANSPORT(cls) -> "HLLWeapon":
        """*ZIS-5 (Transport)*"""
        return cls(
            id="ZIS-5 (Transport)",
            name="ZIS-5 (Transport)",
            vehicle_id="ZIS-5 (Transport)",
            factions={HLLFaction.SOV},
            type=HLLWeaponType.ROADKILL,
        )

    ### INJECT "hll vehicles" END

    # --- Miscellaneous weapons ---

    @class_cached_property
    @classmethod
    def UNKNOWN(cls) -> "HLLWeapon":
        """*UNKNOWN*"""
        return cls(
            id="UNKNOWN",
            name="Unknown",
            factions=set(HLLFaction.all()),
            type=HLLWeaponType.UNKNOWN,
        )

    @class_cached_property
    @classmethod
    def BOMBING_RUN(cls) -> "HLLWeapon":
        """*BOMBING RUN*"""
        return cls(
            id="BOMBING RUN",
            name="Bombing Run",
            factions=set(HLLFaction.all()) - {HLLFaction.SOV},
            type=HLLWeaponType.COMMANDER_ABILITY,
        )

    @class_cached_property
    @classmethod
    def STRAFING_RUN(cls) -> "HLLWeapon":
        """*STRAFING RUN*"""
        return cls(
            id="STRAFING RUN",
            name="Strafing Run",
            factions=set(HLLFaction.all()),
            type=HLLWeaponType.COMMANDER_ABILITY,
        )

    @class_cached_property
    @classmethod
    def PRECISION_STRIKE(cls) -> "HLLWeapon":
        """*PRECISION STRIKE*"""
        return cls(
            id="PRECISION STRIKE",
            name="Precision Strike",
            factions=set(HLLFaction.all()),
            type=HLLWeaponType.COMMANDER_ABILITY,
        )

    @class_cached_property
    @classmethod
    def ARTILLERY_STRIKE(cls) -> "HLLWeapon":
        """*Unknown*"""
        return cls(
            id="Unknown",
            name="Artillery Strike",
            factions=set(HLLFaction.all()),
            type=HLLWeaponType.COMMANDER_ABILITY,
        )

    @class_cached_property
    @classmethod
    def KATYUSHA_BARRAGE(cls) -> "HLLWeapon":
        """*Unknown*"""
        return cls.ARTILLERY_STRIKE

    @class_cached_property
    @classmethod
    def FIRE_SPOT(cls) -> "HLLWeapon":
        """*FireSpot*"""
        return cls(
            id="FireSpot",
            name="Fire",
            factions=set(HLLFaction.all()),
            type=HLLWeaponType.UNKNOWN,
        )


class HLLVWeapon(_Weapon[HLLVFaction, HLLVWeaponType, "HLLVVehicle"]):
    # @computed_field(repr=False)
    @cached_property
    def vehicle(self) -> "HLLVVehicle | None":
        from hllrcon.data.vehicles import HLLVVehicle  # noqa: PLC0415

        if self.vehicle_id:
            return HLLVVehicle.by_id(self.vehicle_id)
        return None


Weapon: TypeAlias = HLLWeapon | HLLVWeapon
