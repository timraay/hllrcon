# ruff: noqa: N802, D400, D415, RUF001, RUF002

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
VehicleT = TypeVar("VehicleT", bound="_Vehicle")


class WeaponType(StrEnum):
    BOLT_ACTION_RIFLE = "Bolt Action Rifle"
    SEMI_AUTO_RIFLE = "Semi-Auto Rifle"
    ASSAULT_RIFLE = "Assault Rifle"
    SUBMACHINE_GUN = "Submachine Gun"
    MACHINE_GUN = "Machine Gun"
    SHOTGUN = "Shotgun"
    PISTOL = "Pistol"
    REVOLVER = "Revolver"
    GRENADE = "Grenade"
    GRENADE_LAUNCHER = "Grenade Launcher"
    AP_MINE = "Anti-Personnel Mine"
    AT_MINE = "Anti-Tank Mine"
    FLAMETHROWER = "Flamethrower"
    MELEE = "Melee"
    RECON_FLARE = "Recon Flare"
    ROCKET_LAUNCHER = "Rocket Launcher"
    ANTI_MATERIEL_RIFLE = "Anti-Materiel Rifle"
    AT_GUN = "Anti-Tank Gun"
    TANK_CANNON = "Tank Cannon"
    TANK_COAXIAL_MG = "Tank Coaxial MG"
    TANK_HULL_MG = "Tank Hull MG"
    TANK_RECON = "Tank Recon"
    TANK_SMOKE_SCREEN = "Tank Smoke Screen"
    MOUNTED_MG = "Mounted MG"
    ROADKILL = "Roadkill"
    ARTILLERY = "Artillery"
    MORTAR = "Mortar"
    COMMANDER_ABILITY = "Commander Ability"
    SATCHEL = "Satchel"
    SMOKE_GRENADE = "Smoke"
    HEALING = "Healing"
    BINOCULARS = "Binoculars"
    SUPPLIES = "Supplies"
    HAMMER = "Hammer"
    WRENCH = "Wrench"
    TORCH = "Torch"
    WATCH = "Watch"
    UNKNOWN = "Unknown"


class _Weapon(IndexedBaseModel[str], Generic[FactionT, VehicleT]):
    id: str
    name: str
    type: WeaponType
    vehicle_id: str | None = None
    factions: Annotated[
        set[FactionT],
        Field(min_length=1),
        model_sequence_serializer(int),
    ]
    magnification: int | None = None

    @property
    def is_lethal(self) -> bool:
        return self.type not in {
            WeaponType.TANK_RECON,
            WeaponType.TANK_SMOKE_SCREEN,
            WeaponType.SMOKE_GRENADE,
            WeaponType.HEALING,
            WeaponType.BINOCULARS,
            WeaponType.SUPPLIES,
            WeaponType.HAMMER,
            WeaponType.WRENCH,
            WeaponType.TORCH,
            WeaponType.WATCH,
        }


class HLLWeapon(_Weapon[HLLFaction, "HLLVehicle"]):
    # @computed_field(repr=False)
    @cached_property
    def vehicle(self) -> "HLLVehicle | None":
        from hllrcon.data.vehicles import HLLVehicle  # noqa: PLC0415

        if self.vehicle_id:
            return HLLVehicle.by_id(self.vehicle_id)
        return None

    ### INJECT "hll loadouts" START

    @class_cached_property
    @classmethod
    def AP_SHRAPNEL_MINE_MK_II(cls) -> "HLLWeapon":
        """*A.P. Shrapnel Mine Mk II*"""
        return cls(
            id="A.P. Shrapnel Mine Mk II",
            name="AP Shrapnel Mine Mk II",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.AP_MINE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def AT_MINE_GS_MK_V(cls) -> "HLLWeapon":
        """*A.T. Mine G.S. Mk V*"""
        return cls(
            id="A.T. Mine G.S. Mk V",
            name="AT Mine G.S. Mk V",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.AT_MINE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def BANDAGE(cls) -> "HLLWeapon":
        """*BANDAGE*"""
        return cls(
            id="BANDAGE",
            name="Bandage",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.US, HLLFaction.SOV, HLLFaction.DAK},
            type=WeaponType.HEALING,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def BANDAGE_2(cls) -> "HLLWeapon":
        """*Bandage*"""
        return cls(
            id="Bandage",
            name="Bandage",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.HEALING,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def BAZOOKA(cls) -> "HLLWeapon":
        """*BAZOOKA*"""
        return cls(
            id="BAZOOKA",
            name="Bazooka",
            vehicle_id=None,
            factions={HLLFaction.US, HLLFaction.SOV},
            type=WeaponType.ROCKET_LAUNCHER,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def BOYS_ANTI_TANK_RIFLE(cls) -> "HLLWeapon":
        """*Boys Anti-tank Rifle*"""
        return cls(
            id="Boys Anti-tank Rifle",
            name="Boys AT Rifle",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.ANTI_MATERIEL_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def BREN_GUN(cls) -> "HLLWeapon":
        """*Bren Gun*"""
        return cls(
            id="Bren Gun",
            name="Bren Gun",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.ASSAULT_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def BROWNING_M1919(cls) -> "HLLWeapon":
        """*BROWNING M1919*"""
        return cls(
            id="BROWNING M1919",
            name="M1919 Browning",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.MACHINE_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def COLT_M1911(cls) -> "HLLWeapon":
        """*COLT M1911*"""
        return cls(
            id="COLT M1911",
            name="Colt M1911",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.PISTOL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def DIENSTGLAS_6_30(cls) -> "HLLWeapon":
        """*DIENSTGLAS 6×30*"""
        return cls(
            id="DIENSTGLAS 6×30",
            name="Dienstglas 6x30",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.BINOCULARS,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def DP_27(cls) -> "HLLWeapon":
        """*DP-27*"""
        return cls(
            id="DP-27",
            name="DP-27",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.MACHINE_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def EXPLOSIVE_AMMO_BOX(cls) -> "HLLWeapon":
        """*EXPLOSIVE AMMO BOX*"""
        return cls(
            id="EXPLOSIVE AMMO BOX",
            name="Explosive Ammo Box",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.US, HLLFaction.SOV, HLLFaction.DAK},
            type=WeaponType.SUPPLIES,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def EXPLOSIVE_AMMO_BOX_2(cls) -> "HLLWeapon":
        """*Explosive Ammo Box*"""
        return cls(
            id="Explosive Ammo Box",
            name="Explosive Ammo Box",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.SUPPLIES,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def EXTERIOR_CUSTOMIZATION(cls) -> "HLLWeapon":
        """*EXTERIOR CUSTOMIZATION*"""
        return cls(
            id="EXTERIOR CUSTOMIZATION",
            name="Exterior Customization",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.US, HLLFaction.SOV, HLLFaction.B8A},
            type=WeaponType.WRENCH,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def FAIRBAIRN_SYKES(cls) -> "HLLWeapon":
        """*Fairbairn–Sykes*"""
        return cls(
            id="Fairbairn–Sykes",
            name="Fairbairn-Sykes",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.MELEE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def FELDSPATEN(cls) -> "HLLWeapon":
        """*FELDSPATEN*"""
        return cls(
            id="FELDSPATEN",
            name="Feldspaten",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.MELEE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def FG42(cls) -> "HLLWeapon":
        """*FG42*"""
        return cls(
            id="FG42",
            name="FG42",
            vehicle_id=None,
            factions={HLLFaction.GER},
            type=WeaponType.ASSAULT_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def FG42_X4(cls) -> "HLLWeapon":
        """*FG42 x4*"""
        return cls(
            id="FG42 x4",
            name="FG42",
            vehicle_id=None,
            factions={HLLFaction.GER},
            type=WeaponType.SEMI_AUTO_RIFLE,
            magnification=4,
        )

    @class_cached_property
    @classmethod
    def FLAMETHROWER(cls) -> "HLLWeapon":
        """*FLAMETHROWER*"""
        return cls(
            id="FLAMETHROWER",
            name="Lifebuoy Flamethrower",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.FLAMETHROWER,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def FLAMMENWERFER_41(cls) -> "HLLWeapon":
        """*FLAMMENWERFER 41*"""
        return cls(
            id="FLAMMENWERFER 41",
            name="Flammenwerfer 41",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.FLAMETHROWER,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def FLARE_GUN(cls) -> "HLLWeapon":
        """*FLARE GUN*"""
        return cls(
            id="FLARE GUN",
            name="Flare Gun",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.US, HLLFaction.SOV, HLLFaction.DAK},
            type=WeaponType.RECON_FLARE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def GEWEHR_43(cls) -> "HLLWeapon":
        """*GEWEHR 43*"""
        return cls(
            id="GEWEHR 43",
            name="G43",
            vehicle_id=None,
            factions={HLLFaction.GER},
            type=WeaponType.SEMI_AUTO_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def HAMMER(cls) -> "HLLWeapon":
        """*HAMMER*"""
        return cls(
            id="HAMMER",
            name="Hammer",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.US, HLLFaction.SOV, HLLFaction.DAK},
            type=WeaponType.HAMMER,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def HAMMER_2(cls) -> "HLLWeapon":
        """*Hammer*"""
        return cls(
            id="Hammer",
            name="Hammer",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.HAMMER,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def KARABINER_98K(cls) -> "HLLWeapon":
        """*KARABINER 98K*"""
        return cls(
            id="KARABINER 98K",
            name="Karabiner 98k",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def KARABINER_98K_X8(cls) -> "HLLWeapon":
        """*KARABINER 98K x8*"""
        return cls(
            id="KARABINER 98K x8",
            name="Karabiner 98k",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=8,
        )

    @class_cached_property
    @classmethod
    def LEWIS_GUN(cls) -> "HLLWeapon":
        """*Lewis Gun*"""
        return cls(
            id="Lewis Gun",
            name="Lewis Gun",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.MACHINE_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def LUGER_P08(cls) -> "HLLWeapon":
        """*LUGER P08*"""
        return cls(
            id="LUGER P08",
            name="Luger P08",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.PISTOL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M18_SMOKE_GRENADE(cls) -> "HLLWeapon":
        """*M18 SMOKE GRENADE*"""
        return cls(
            id="M18 SMOKE GRENADE",
            name="M18 Smoke Grenade",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.SMOKE_GRENADE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M1903_SPRINGFIELD(cls) -> "HLLWeapon":
        """*M1903 SPRINGFIELD*"""
        return cls(
            id="M1903 SPRINGFIELD",
            name="M1903 Springfield",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=4,
        )

    @class_cached_property
    @classmethod
    def M1918A2_BAR(cls) -> "HLLWeapon":
        """*M1918A2 BAR*"""
        return cls(
            id="M1918A2 BAR",
            name="M1918A2 BAR",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.ASSAULT_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M1928A1_THOMPSON(cls) -> "HLLWeapon":
        """*M1928A1 THOMPSON*"""
        return cls(
            id="M1928A1 THOMPSON",
            name="M1928A1 Thompson",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.SUBMACHINE_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M1A1_AT_MINE(cls) -> "HLLWeapon":
        """*M1A1 AT MINE*"""
        return cls(
            id="M1A1 AT MINE",
            name="M1A1 AT Mine",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.AT_MINE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M1A1_THOMPSON(cls) -> "HLLWeapon":
        """*M1A1 THOMPSON*"""
        return cls(
            id="M1A1 THOMPSON",
            name="M1A1 Thompson",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.SUBMACHINE_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M1_CARBINE(cls) -> "HLLWeapon":
        """*M1 CARBINE*"""
        return cls(
            id="M1 CARBINE",
            name="M1 Carbine",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.SEMI_AUTO_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M1_GARAND(cls) -> "HLLWeapon":
        """*M1 GARAND*"""
        return cls(
            id="M1 GARAND",
            name="M1 Garand",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.SEMI_AUTO_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M24_STIELHANDGRANATE(cls) -> "HLLWeapon":
        """*M24 STIELHANDGRANATE*"""
        return cls(
            id="M24 STIELHANDGRANATE",
            name="M24 Stielhandgranate",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.GRENADE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M2_AP_MINE(cls) -> "HLLWeapon":
        """*M2 AP MINE*"""
        return cls(
            id="M2 AP MINE",
            name="M2 AP Mine",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.AP_MINE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M2_FLAMETHROWER(cls) -> "HLLWeapon":
        """*M2 FLAMETHROWER*"""
        return cls(
            id="M2 FLAMETHROWER",
            name="M2 Flamethrower",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.FLAMETHROWER,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M3_GREASE_GUN(cls) -> "HLLWeapon":
        """*M3 GREASE GUN*"""
        return cls(
            id="M3 GREASE GUN",
            name="M3 Grease Gun",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.SUBMACHINE_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M3_KNIFE(cls) -> "HLLWeapon":
        """*M3 KNIFE*"""
        return cls(
            id="M3 KNIFE",
            name="M3 Knife",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.MELEE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M43_STIELHANDGRANATE(cls) -> "HLLWeapon":
        """*M43 STIELHANDGRANATE*"""
        return cls(
            id="M43 STIELHANDGRANATE",
            name="M43 Stielhandgranate",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.GRENADE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M97_TRENCH_GUN(cls) -> "HLLWeapon":
        """*M97 TRENCH GUN*"""
        return cls(
            id="M97 TRENCH GUN",
            name="M97 Trench Gun",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.SHOTGUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def MEDICAL_SUPPLIES(cls) -> "HLLWeapon":
        """*MEDICAL SUPPLIES*"""
        return cls(
            id="MEDICAL SUPPLIES",
            name="Medical Supplies",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.US, HLLFaction.SOV, HLLFaction.DAK},
            type=WeaponType.SUPPLIES,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def MEDICAL_SUPPLIES_2(cls) -> "HLLWeapon":
        """*Medical Supplies*"""
        return cls(
            id="Medical Supplies",
            name="Medical Supplies",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.SUPPLIES,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def MG34(cls) -> "HLLWeapon":
        """*MG34*"""
        return cls(
            id="MG34",
            name="MG34",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.MACHINE_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def MG42(cls) -> "HLLWeapon":
        """*MG42*"""
        return cls(
            id="MG42",
            name="MG42",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.MACHINE_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def MILLS_BOMB(cls) -> "HLLWeapon":
        """*Mills Bomb*"""
        return cls(
            id="Mills Bomb",
            name="Mills Bomb",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.GRENADE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def MK2_GRENADE(cls) -> "HLLWeapon":
        """*MK2 GRENADE*"""
        return cls(
            id="MK2 GRENADE",
            name="Mk 2 Grenade",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.GRENADE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def MOLOTOV(cls) -> "HLLWeapon":
        """*MOLOTOV*"""
        return cls(
            id="MOLOTOV",
            name="Molotov",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.GRENADE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def MORPHINE(cls) -> "HLLWeapon":
        """*Morphine*"""
        return cls(
            id="Morphine",
            name="Morphine",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.HEALING,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def MORPHINE_AMPOULE(cls) -> "HLLWeapon":
        """*MORPHINE AMPOULE*"""
        return cls(
            id="MORPHINE AMPOULE",
            name="Morphine",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.HEALING,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def MORPHINE_SYRETTE(cls) -> "HLLWeapon":
        """*MORPHINE SYRETTE*"""
        return cls(
            id="MORPHINE SYRETTE",
            name="Morphine Syrette",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.HEALING,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def MOSIN_NAGANT_1891(cls) -> "HLLWeapon":
        """*MOSIN NAGANT 1891*"""
        return cls(
            id="MOSIN NAGANT 1891",
            name="Mosin-Nagant 1891",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def MOSIN_NAGANT_91_30(cls) -> "HLLWeapon":
        """*MOSIN NAGANT 91/30*"""
        return cls(
            id="MOSIN NAGANT 91/30",
            name="Mosin-Nagant 91/30",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def MOSIN_NAGANT_M38(cls) -> "HLLWeapon":
        """*MOSIN NAGANT M38*"""
        return cls(
            id="MOSIN NAGANT M38",
            name="Mosin-Nagant M38",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def MP40(cls) -> "HLLWeapon":
        """*MP40*"""
        return cls(
            id="MP40",
            name="MP40",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.SUBMACHINE_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def MPL_50_SPADE(cls) -> "HLLWeapon":
        """*MPL-50 SPADE*"""
        return cls(
            id="MPL-50 SPADE",
            name="MPL-50 Spade",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.MELEE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def NAGANT_M1895(cls) -> "HLLWeapon":
        """*NAGANT M1895*"""
        return cls(
            id="NAGANT M1895",
            name="Nagant M1895",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.REVOLVER,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def NB39_NEBELHANDGRANATE(cls) -> "HLLWeapon":
        """*NB39 NEBELHANDGRANATE*"""
        return cls(
            id="NB39 NEBELHANDGRANATE",
            name="NB39 Nebelhandgranate",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.SMOKE_GRENADE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def NO_2_MK_5_FLARE_PISTOL(cls) -> "HLLWeapon":
        """*No.2 Mk 5 Flare Pistol*"""
        return cls(
            id="No.2 Mk 5 Flare Pistol",
            name="No.2 Mk V Flare Gun",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.RECON_FLARE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def NO_77(cls) -> "HLLWeapon":
        """*No.77*"""
        return cls(
            id="No.77",
            name="No.77 WP Grenade",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.SMOKE_GRENADE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def NO_82_GRENADE(cls) -> "HLLWeapon":
        """*No.82 Grenade*"""
        return cls(
            id="No.82 Grenade",
            name="Gammon Bomb",
            vehicle_id=None,
            factions={HLLFaction.CW},
            type=WeaponType.GRENADE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def ORDNANCE_QF_6_POUNDER(cls) -> "HLLWeapon":
        """*Ordnance QF 6-pounder*"""
        return cls(
            id="Ordnance QF 6-pounder",
            name="Ordnance QF 6-pounder",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.WRENCH,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def PAK_40(cls) -> "HLLWeapon":
        """*PAK 40*"""
        return cls(
            id="PAK 40",
            name="Wrench",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.WRENCH,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def PANZERSCHRECK(cls) -> "HLLWeapon":
        """*PANZERSCHRECK*"""
        return cls(
            id="PANZERSCHRECK",
            name="Panzerschreck",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.ROCKET_LAUNCHER,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def PIAT(cls) -> "HLLWeapon":
        """*PIAT*"""
        return cls(
            id="PIAT",
            name="PIAT",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.ROCKET_LAUNCHER,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def POMZ_AP_MINE(cls) -> "HLLWeapon":
        """*POMZ AP MINE*"""
        return cls(
            id="POMZ AP MINE",
            name="POMZ AP Mine",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.AP_MINE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def PPSH_41(cls) -> "HLLWeapon":
        """*PPSH 41*"""
        return cls(
            id="PPSH 41",
            name="PPSh-41",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.SUBMACHINE_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def PPSH_41_W_DRUM(cls) -> "HLLWeapon":
        """*PPSH 41 W/DRUM*"""
        return cls(
            id="PPSH 41 W/DRUM",
            name="PPSh-41 with Drum",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.SUBMACHINE_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def PRISM_NO_2_MK_II_X6(cls) -> "HLLWeapon":
        """*Prism No.2 Mk II x6*"""
        return cls(
            id="Prism No.2 Mk II x6",
            name="Prism No.2 Mk II x6",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.BINOCULARS,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def PTRS_41(cls) -> "HLLWeapon":
        """*PTRS-41*"""
        return cls(
            id="PTRS-41",
            name="PTRS-41",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.ANTI_MATERIEL_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def RDG_2_SMOKE(cls) -> "HLLWeapon":
        """*RDG-2 SMOKE*"""
        return cls(
            id="RDG-2 SMOKE",
            name="RDG-2 Smoke Grenade",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.SMOKE_GRENADE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def REVIVE(cls) -> "HLLWeapon":
        """*REVIVE*"""
        return cls(
            id="REVIVE",
            name="Revive",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.HEALING,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def RG_42_GRENADE(cls) -> "HLLWeapon":
        """*RG-42 GRENADE*"""
        return cls(
            id="RG-42 GRENADE",
            name="RG-42 Grenade",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.GRENADE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def RIFLE_NO_4_MK_I(cls) -> "HLLWeapon":
        """*Rifle No.4 Mk I*"""
        return cls(
            id="Rifle No.4 Mk I",
            name="No.4 Rifle Mk I",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def RIFLE_NO_4_MK_I_SNIPER(cls) -> "HLLWeapon":
        """*Rifle No.4 Mk I Sniper*"""
        return cls(
            id="Rifle No.4 Mk I Sniper",
            name="No.4 Rifle Mk I",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=8,
        )

    @class_cached_property
    @classmethod
    def RKKA_8_40(cls) -> "HLLWeapon":
        """*RKKA 8×40*"""
        return cls(
            id="RKKA 8×40",
            name="RKKA 8x40",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.BINOCULARS,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def SATCHEL(cls) -> "HLLWeapon":
        """*SATCHEL*"""
        return cls(
            id="SATCHEL",
            name="Satchel Charge",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.US, HLLFaction.DAK},
            type=WeaponType.SATCHEL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def SATCHEL_2(cls) -> "HLLWeapon":
        """*Satchel*"""
        return cls(
            id="Satchel",
            name="Satchel Charge",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.SATCHEL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def SATCHEL_CHARGE(cls) -> "HLLWeapon":
        """*SATCHEL CHARGE*"""
        return cls(
            id="SATCHEL CHARGE",
            name="Satchel Charge",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.SATCHEL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def SCOPED_MOSIN_NAGANT_91_30(cls) -> "HLLWeapon":
        """*SCOPED MOSIN NAGANT 91/30*"""
        return cls(
            id="SCOPED MOSIN NAGANT 91/30",
            name="Mosin-Nagant 91/30",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=4,
        )

    @class_cached_property
    @classmethod
    def SCOPED_SVT40(cls) -> "HLLWeapon":
        """*SCOPED SVT40*"""
        return cls(
            id="SCOPED SVT40",
            name="SVT-40",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.SEMI_AUTO_RIFLE,
            magnification=4,
        )

    @class_cached_property
    @classmethod
    def SMALL_AMMUNITION_BOX(cls) -> "HLLWeapon":
        """*SMALL AMMUNITION BOX*"""
        return cls(
            id="SMALL AMMUNITION BOX",
            name="Small Ammunition Box",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.US, HLLFaction.SOV, HLLFaction.DAK},
            type=WeaponType.SUPPLIES,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def SMALL_AMMUNITION_BOX_2(cls) -> "HLLWeapon":
        """*Small Ammunition Box*"""
        return cls(
            id="Small Ammunition Box",
            name="Small Ammunition Box",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.SUPPLIES,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def SMLE_NO_1_MK_III(cls) -> "HLLWeapon":
        """*SMLE No.1 Mk III*"""
        return cls(
            id="SMLE No.1 Mk III",
            name="SMLE Mk III",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def STEN_GUN_MK_II(cls) -> "HLLWeapon":
        """*Sten Gun Mk.II*"""
        return cls(
            id="Sten Gun Mk.II",
            name="Sten Mk II",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.SUBMACHINE_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def STEN_GUN_MK_V(cls) -> "HLLWeapon":
        """*Sten Gun Mk.V*"""
        return cls(
            id="Sten Gun Mk.V",
            name="Sten Mk V",
            vehicle_id=None,
            factions={HLLFaction.CW},
            type=WeaponType.SUBMACHINE_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def STG44(cls) -> "HLLWeapon":
        """*STG44*"""
        return cls(
            id="STG44",
            name="STG44",
            vehicle_id=None,
            factions={HLLFaction.GER},
            type=WeaponType.ASSAULT_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def SUPPLIES(cls) -> "HLLWeapon":
        """*SUPPLIES*"""
        return cls(
            id="SUPPLIES",
            name="Supplies",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.US, HLLFaction.SOV, HLLFaction.DAK},
            type=WeaponType.SUPPLIES,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def SUPPLIES_2(cls) -> "HLLWeapon":
        """*Supplies*"""
        return cls(
            id="Supplies",
            name="Supplies",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.SUPPLIES,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def SVT40(cls) -> "HLLWeapon":
        """*SVT40*"""
        return cls(
            id="SVT40",
            name="SVT-40",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.SEMI_AUTO_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def S_MINE(cls) -> "HLLWeapon":
        """*S-MINE*"""
        return cls(
            id="S-MINE",
            name="S-Mine",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.AP_MINE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def TELLERMINE_43(cls) -> "HLLWeapon":
        """*TELLERMINE 43*"""
        return cls(
            id="TELLERMINE 43",
            name="Tellermine 43",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.AT_MINE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def TM_35_AT_MINE(cls) -> "HLLWeapon":
        """*TM-35 AT MINE*"""
        return cls(
            id="TM-35 AT MINE",
            name="TM-35 AT Mine",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.AT_MINE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def TOKAREV_TT33(cls) -> "HLLWeapon":
        """*TOKAREV TT33*"""
        return cls(
            id="TOKAREV TT33",
            name="Tokarev TT-33",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.PISTOL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def TORCH(cls) -> "HLLWeapon":
        """*TORCH*"""
        return cls(
            id="TORCH",
            name="Torch",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.US, HLLFaction.SOV, HLLFaction.DAK},
            type=WeaponType.TORCH,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def TORCH_2(cls) -> "HLLWeapon":
        """*Torch*"""
        return cls(
            id="Torch",
            name="Torch",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.TORCH,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def WALTHER_P38(cls) -> "HLLWeapon":
        """*WALTHER P38*"""
        return cls(
            id="WALTHER P38",
            name="Walther P38",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.PISTOL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def WATCH(cls) -> "HLLWeapon":
        """*WATCH*"""
        return cls(
            id="WATCH",
            name="Watch",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.US, HLLFaction.SOV, HLLFaction.DAK},
            type=WeaponType.WATCH,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def WATCH_2(cls) -> "HLLWeapon":
        """*Watch*"""
        return cls(
            id="Watch",
            name="Watch",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.WATCH,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def WEBLEY_MK_VI(cls) -> "HLLWeapon":
        """*Webley MK VI*"""
        return cls(
            id="Webley MK VI",
            name="Webley Mk IV",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.REVOLVER,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def WESTINGHOUSE_M3_6_30(cls) -> "HLLWeapon":
        """*WESTINGHOUSE M3 6×30*"""
        return cls(
            id="WESTINGHOUSE M3 6×30",
            name="Westinghouse M3 6x30",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.BINOCULARS,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def WRENCH(cls) -> "HLLWeapon":
        """*WRENCH*"""
        return cls(
            id="WRENCH",
            name="Wrench",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.US, HLLFaction.SOV, HLLFaction.DAK},
            type=WeaponType.WRENCH,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def WRENCH_2(cls) -> "HLLWeapon":
        """*Wrench*"""
        return cls(
            id="Wrench",
            name="Wrench",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.WRENCH,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def WRENCH_57MM_M1(cls) -> "HLLWeapon":
        """*57MM M1*"""
        return cls(
            id="57MM M1",
            name="Wrench",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.WRENCH,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def ZIS_2(cls) -> "HLLWeapon":
        """*ZiS-2*"""
        return cls(
            id="ZiS-2",
            name="ZiS-2",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.WRENCH,
            magnification=None,
        )

    ### INJECT "hll loadouts" END
    ### INJECT "hll vehicles" START

    @class_cached_property
    @classmethod
    def V_105MM_HOWITZER__UNKNOWN(cls) -> "HLLWeapon":
        """*105MM HOWITZER*"""
        return cls(
            id="105MM HOWITZER",
            name="105mm Howitzer",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_105MM_HOWITZER__M4A3_105MM(cls) -> "HLLWeapon":
        """*105MM HOWITZER [M4A3 (105mm)]*"""
        return cls(
            id="105MM HOWITZER [M4A3 (105mm)]",
            name="105mm Howitzer",
            vehicle_id="M4A3 (105mm)",
            factions={HLLFaction.US},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_122MM_HOWITZER__UNKNOWN(cls) -> "HLLWeapon":
        """*122MM HOWITZER*"""
        return cls(
            id="122MM HOWITZER",
            name="122mm Howitzer",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.ARTILLERY,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_122MM_HOWITZER__M1938_M_30(cls) -> "HLLWeapon":
        """*122MM HOWITZER [M1938 (M-30)]*"""
        return cls(
            id="122MM HOWITZER [M1938 (M-30)]",
            name="122mm Howitzer",
            vehicle_id="M1938 (M-30)",
            factions={HLLFaction.SOV},
            type=WeaponType.ARTILLERY,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_150MM_HOWITZER__UNKNOWN(cls) -> "HLLWeapon":
        """*150MM HOWITZER*"""
        return cls(
            id="150MM HOWITZER",
            name="150mm Howitzer",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.ARTILLERY,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_150MM_HOWITZER__SFH_18(cls) -> "HLLWeapon":
        """*150MM HOWITZER [sFH 18]*"""
        return cls(
            id="150MM HOWITZER [sFH 18]",
            name="150mm Howitzer",
            vehicle_id="sFH 18",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.ARTILLERY,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_152MM_M_10T__UNKNOWN(cls) -> "HLLWeapon":
        """*152MM M-10T*"""
        return cls(
            id="152MM M-10T",
            name="M-10T 152mm",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_152MM_M_10T__KV_2(cls) -> "HLLWeapon":
        """*152MM M-10T [KV-2]*"""
        return cls(
            id="152MM M-10T [KV-2]",
            name="M-10T 152mm",
            vehicle_id="KV-2",
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_155MM_HOWITZER__UNKNOWN(cls) -> "HLLWeapon":
        """*155MM HOWITZER*"""
        return cls(
            id="155MM HOWITZER",
            name="155mm Howitzer",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.ARTILLERY,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_155MM_HOWITZER__M114(cls) -> "HLLWeapon":
        """*155MM HOWITZER [M114]*"""
        return cls(
            id="155MM HOWITZER [M114]",
            name="155mm Howitzer",
            vehicle_id="M114",
            factions={HLLFaction.US},
            type=WeaponType.ARTILLERY,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_19_K_45MM__UNKNOWN(cls) -> "HLLWeapon":
        """*19-K 45MM*"""
        return cls(
            id="19-K 45MM",
            name="45mm M1932",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_19_K_45MM__BA_10(cls) -> "HLLWeapon":
        """*19-K 45MM [BA-10]*"""
        return cls(
            id="19-K 45MM [BA-10]",
            name="45mm M1932",
            vehicle_id="BA-10",
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_20MM_KWK_30__UNKNOWN(cls) -> "HLLWeapon":
        """*20MM KWK 30*"""
        return cls(
            id="20MM KWK 30",
            name="20mm KwK 30",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_20MM_KWK_30__SD_KFZ_121_LUCHS(cls) -> "HLLWeapon":
        """*20MM KWK 30 [Sd.Kfz.121 Luchs]*"""
        return cls(
            id="20MM KWK 30 [Sd.Kfz.121 Luchs]",
            name="20mm KwK 30",
            vehicle_id="Sd.Kfz.121 Luchs",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_230MM_PETARD__UNKNOWN(cls) -> "HLLWeapon":
        """*230MM PETARD*"""
        return cls(
            id="230MM PETARD",
            name="230mm Petard",
            vehicle_id=None,
            factions={HLLFaction.CW},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_230MM_PETARD__CHURCHILL_MK_III_A_V_R_E(cls) -> "HLLWeapon":
        """*230MM PETARD [Churchill Mk III A.V.R.E.]*"""
        return cls(
            id="230MM PETARD [Churchill Mk III A.V.R.E.]",
            name="230mm Petard",
            vehicle_id="Churchill Mk III A.V.R.E.",
            factions={HLLFaction.CW},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_37MM_CANNON__UNKNOWN(cls) -> "HLLWeapon":
        """*37MM CANNON*"""
        return cls(
            id="37MM CANNON",
            name="37mm Cannon",
            vehicle_id=None,
            factions={HLLFaction.US, HLLFaction.B8A},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_37MM_CANNON__M3_STUART_HONEY(cls) -> "HLLWeapon":
        """*37MM CANNON [M3 Stuart Honey]*"""
        return cls(
            id="37MM CANNON [M3 Stuart Honey]",
            name="37mm Cannon",
            vehicle_id="M3 Stuart Honey",
            factions={HLLFaction.B8A},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_37MM_CANNON__STUART_M5A1(cls) -> "HLLWeapon":
        """*37MM CANNON [Stuart M5A1]*"""
        return cls(
            id="37MM CANNON [Stuart M5A1]",
            name="37mm Cannon",
            vehicle_id="Stuart M5A1",
            factions={HLLFaction.US},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_45MM_M1937__UNKNOWN(cls) -> "HLLWeapon":
        """*45MM M1937*"""
        return cls(
            id="45MM M1937",
            name="45mm M1937",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_45MM_M1937__T70(cls) -> "HLLWeapon":
        """*45MM M1937 [T70]*"""
        return cls(
            id="45MM M1937 [T70]",
            name="45mm M1937",
            vehicle_id="T70",
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_CANNON,
            magnification=None,
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
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_50MM_KWK_39_1__SD_KFZ_234_PUMA(cls) -> "HLLWeapon":
        """*50mm KwK 39/1 [Sd.Kfz.234 Puma]*"""
        return cls(
            id="50mm KwK 39/1 [Sd.Kfz.234 Puma]",
            name="50mm KwK 39/1",
            vehicle_id="Sd.Kfz.234 Puma",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_57MM_CANNON__UNKNOWN(cls) -> "HLLWeapon":
        """*57MM CANNON*"""
        return cls(
            id="57MM CANNON",
            name="57mm Cannon",
            vehicle_id=None,
            factions={HLLFaction.US, HLLFaction.SOV},
            type=WeaponType.AT_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_57MM_CANNON__M1_57MM(cls) -> "HLLWeapon":
        """*57MM CANNON [M1 57mm]*"""
        return cls(
            id="57MM CANNON [M1 57mm]",
            name="57mm Cannon",
            vehicle_id="M1 57mm",
            factions={HLLFaction.US},
            type=WeaponType.AT_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_57MM_CANNON__ZIS_2(cls) -> "HLLWeapon":
        """*57MM CANNON [ZiS-2]*"""
        return cls(
            id="57MM CANNON [ZiS-2]",
            name="57mm Cannon",
            vehicle_id="ZiS-2",
            factions={HLLFaction.SOV},
            type=WeaponType.AT_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_7_5CM_KWK_37__UNKNOWN(cls) -> "HLLWeapon":
        """*7.5CM KwK 37*"""
        return cls(
            id="7.5CM KwK 37",
            name="75mm KwK 37",
            vehicle_id=None,
            factions={HLLFaction.DAK},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_7_5CM_KWK_37__PANZER_III_AUSF_N(cls) -> "HLLWeapon":
        """*7.5CM KwK 37 [Panzer III Ausf.N]*"""
        return cls(
            id="7.5CM KwK 37 [Panzer III Ausf.N]",
            name="75mm KwK 37",
            vehicle_id="Panzer III Ausf.N",
            factions={HLLFaction.DAK},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_75MM_CANNON__UNKNOWN(cls) -> "HLLWeapon":
        """*75MM CANNON*"""
        return cls(
            id="75MM CANNON",
            name="75mm Cannon",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.US, HLLFaction.DAK},
            type=WeaponType.UNKNOWN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_75MM_CANNON__PAK_40(cls) -> "HLLWeapon":
        """*75MM CANNON [PAK 40]*"""
        return cls(
            id="75MM CANNON [PAK 40]",
            name="75mm Cannon",
            vehicle_id="PAK 40",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.AT_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_75MM_CANNON__SD_KFZ_161_PANZER_IV(cls) -> "HLLWeapon":
        """*75MM CANNON [Sd.Kfz.161 Panzer IV]*"""
        return cls(
            id="75MM CANNON [Sd.Kfz.161 Panzer IV]",
            name="75mm Cannon",
            vehicle_id="Sd.Kfz.161 Panzer IV",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_75MM_CANNON__SD_KFZ_171_PANTHER(cls) -> "HLLWeapon":
        """*75MM CANNON [Sd.Kfz.171 Panther]*"""
        return cls(
            id="75MM CANNON [Sd.Kfz.171 Panther]",
            name="75mm Cannon",
            vehicle_id="Sd.Kfz.171 Panther",
            factions={HLLFaction.GER},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_75MM_CANNON__SHERMAN_M4A375W(cls) -> "HLLWeapon":
        """*75MM CANNON [Sherman M4A3(75)W]*"""
        return cls(
            id="75MM CANNON [Sherman M4A3(75)W]",
            name="75mm Cannon",
            vehicle_id="Sherman M4A3(75)W",
            factions={HLLFaction.US},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_75MM_M3_GUN__UNKNOWN(cls) -> "HLLWeapon":
        """*75MM M3 GUN*"""
        return cls(
            id="75MM M3 GUN",
            name="75mm Cannon",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_75MM_M3_GUN__SHERMAN_M4A3E2(cls) -> "HLLWeapon":
        """*75MM M3 GUN [Sherman M4A3E2]*"""
        return cls(
            id="75MM M3 GUN [Sherman M4A3E2]",
            name="75mm Cannon",
            vehicle_id="Sherman M4A3E2",
            factions={HLLFaction.US},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_76MM_M1_GUN__UNKNOWN(cls) -> "HLLWeapon":
        """*76MM M1 GUN*"""
        return cls(
            id="76MM M1 GUN",
            name="76mm Cannon",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_76MM_M1_GUN__SHERMAN_M4A3E276(cls) -> "HLLWeapon":
        """*76MM M1 GUN [Sherman M4A3E2(76)]*"""
        return cls(
            id="76MM M1 GUN [Sherman M4A3E2(76)]",
            name="76mm Cannon",
            vehicle_id="Sherman M4A3E2(76)",
            factions={HLLFaction.US},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_76MM_ZIS_5__UNKNOWN(cls) -> "HLLWeapon":
        """*76MM ZiS-5*"""
        return cls(
            id="76MM ZiS-5",
            name="76mm M1940",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_76MM_ZIS_5__T34_76(cls) -> "HLLWeapon":
        """*76MM ZiS-5 [T34/76]*"""
        return cls(
            id="76MM ZiS-5 [T34/76]",
            name="76mm M1940",
            vehicle_id="T34/76",
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_88_KWK_36_L_56__UNKNOWN(cls) -> "HLLWeapon":
        """*88 KWK 36 L/56*"""
        return cls(
            id="88 KWK 36 L/56",
            name="88mm KwK 36 L/56",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_88_KWK_36_L_56__SD_KFZ_181_TIGER_1(cls) -> "HLLWeapon":
        """*88 KWK 36 L/56 [Sd.Kfz.181 Tiger 1]*"""
        return cls(
            id="88 KWK 36 L/56 [Sd.Kfz.181 Tiger 1]",
            name="88mm KwK 36 L/56",
            vehicle_id="Sd.Kfz.181 Tiger 1",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.TANK_CANNON,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA__UNKNOWN(cls) -> "HLLWeapon":
        """*COAXIAL BESA*"""
        return cls(
            id="COAXIAL BESA",
            name="BESA",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA_7_92MM__UNKNOWN(cls) -> "HLLWeapon":
        """*COAXIAL BESA 7.92mm*"""
        return cls(
            id="COAXIAL BESA 7.92mm",
            name="BESA",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA_7_92MM__CHURCHILL_MK_III_A_V_R_E(cls) -> "HLLWeapon":
        """*COAXIAL BESA 7.92mm [Churchill Mk III A.V.R.E.]*"""
        return cls(
            id="COAXIAL BESA 7.92mm [Churchill Mk III A.V.R.E.]",
            name="BESA",
            vehicle_id="Churchill Mk III A.V.R.E.",
            factions={HLLFaction.CW},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA_7_92MM__CHURCHILL_MK_III(cls) -> "HLLWeapon":
        """*COAXIAL BESA 7.92mm [Churchill Mk.III]*"""
        return cls(
            id="COAXIAL BESA 7.92mm [Churchill Mk.III]",
            name="BESA",
            vehicle_id="Churchill Mk.III",
            factions={HLLFaction.B8A},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA_7_92MM__CHURCHILL_MK_VII(cls) -> "HLLWeapon":
        """*COAXIAL BESA 7.92mm [Churchill Mk.VII]*"""
        return cls(
            id="COAXIAL BESA 7.92mm [Churchill Mk.VII]",
            name="BESA",
            vehicle_id="Churchill Mk.VII",
            factions={HLLFaction.CW},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA__CROMWELL(cls) -> "HLLWeapon":
        """*COAXIAL BESA [Cromwell]*"""
        return cls(
            id="COAXIAL BESA [Cromwell]",
            name="BESA",
            vehicle_id="Cromwell",
            factions={HLLFaction.CW},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA__CRUSADER_MK_III(cls) -> "HLLWeapon":
        """*COAXIAL BESA [Crusader Mk.III]*"""
        return cls(
            id="COAXIAL BESA [Crusader Mk.III]",
            name="BESA",
            vehicle_id="Crusader Mk.III",
            factions={HLLFaction.B8A},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA__DAIMLER(cls) -> "HLLWeapon":
        """*COAXIAL BESA [Daimler]*"""
        return cls(
            id="COAXIAL BESA [Daimler]",
            name="BESA",
            vehicle_id="Daimler",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_BESA__TETRARCH(cls) -> "HLLWeapon":
        """*COAXIAL BESA [Tetrarch]*"""
        return cls(
            id="COAXIAL BESA [Tetrarch]",
            name="BESA",
            vehicle_id="Tetrarch",
            factions={HLLFaction.CW},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
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
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_DT__BA_10(cls) -> "HLLWeapon":
        """*COAXIAL DT [BA-10]*"""
        return cls(
            id="COAXIAL DT [BA-10]",
            name="DT",
            vehicle_id="BA-10",
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_DT__IS_1(cls) -> "HLLWeapon":
        """*COAXIAL DT [IS-1]*"""
        return cls(
            id="COAXIAL DT [IS-1]",
            name="DT",
            vehicle_id="IS-1",
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_DT__T34_76(cls) -> "HLLWeapon":
        """*COAXIAL DT [T34/76]*"""
        return cls(
            id="COAXIAL DT [T34/76]",
            name="DT",
            vehicle_id="T34/76",
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_DT__T70(cls) -> "HLLWeapon":
        """*COAXIAL DT [T70]*"""
        return cls(
            id="COAXIAL DT [T70]",
            name="DT",
            vehicle_id="T70",
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__UNKNOWN(cls) -> "HLLWeapon":
        """*COAXIAL M1919*"""
        return cls(
            id="COAXIAL M1919",
            name="M1919 Browning",
            vehicle_id=None,
            factions={HLLFaction.US, HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__FIREFLY(cls) -> "HLLWeapon":
        """*COAXIAL M1919 [Firefly]*"""
        return cls(
            id="COAXIAL M1919 [Firefly]",
            name="M1919 Browning",
            vehicle_id="Firefly",
            factions={HLLFaction.CW},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__M3_STUART_HONEY(cls) -> "HLLWeapon":
        """*COAXIAL M1919 [M3 Stuart Honey]*"""
        return cls(
            id="COAXIAL M1919 [M3 Stuart Honey]",
            name="M1919 Browning",
            vehicle_id="M3 Stuart Honey",
            factions={HLLFaction.B8A},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__M4A3_105MM(cls) -> "HLLWeapon":
        """*COAXIAL M1919 [M4A3 (105mm)]*"""
        return cls(
            id="COAXIAL M1919 [M4A3 (105mm)]",
            name="M1919 Browning",
            vehicle_id="M4A3 (105mm)",
            factions={HLLFaction.US},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__M8_GREYHOUND(cls) -> "HLLWeapon":
        """*COAXIAL M1919 [M8 Greyhound]*"""
        return cls(
            id="COAXIAL M1919 [M8 Greyhound]",
            name="M1919 Browning",
            vehicle_id="M8 Greyhound",
            factions={HLLFaction.US},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__SHERMAN_M4A375W(cls) -> "HLLWeapon":
        """*COAXIAL M1919 [Sherman M4A3(75)W]*"""
        return cls(
            id="COAXIAL M1919 [Sherman M4A3(75)W]",
            name="M1919 Browning",
            vehicle_id="Sherman M4A3(75)W",
            factions={HLLFaction.US},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__SHERMAN_M4A3E276(cls) -> "HLLWeapon":
        """*COAXIAL M1919 [Sherman M4A3E2(76)]*"""
        return cls(
            id="COAXIAL M1919 [Sherman M4A3E2(76)]",
            name="M1919 Browning",
            vehicle_id="Sherman M4A3E2(76)",
            factions={HLLFaction.US},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__SHERMAN_M4A3E2(cls) -> "HLLWeapon":
        """*COAXIAL M1919 [Sherman M4A3E2]*"""
        return cls(
            id="COAXIAL M1919 [Sherman M4A3E2]",
            name="M1919 Browning",
            vehicle_id="Sherman M4A3E2",
            factions={HLLFaction.US},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_M1919__STUART_M5A1(cls) -> "HLLWeapon":
        """*COAXIAL M1919 [Stuart M5A1]*"""
        return cls(
            id="COAXIAL M1919 [Stuart M5A1]",
            name="M1919 Browning",
            vehicle_id="Stuart M5A1",
            factions={HLLFaction.US},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__UNKNOWN(cls) -> "HLLWeapon":
        """*COAXIAL MG34*"""
        return cls(
            id="COAXIAL MG34",
            name="MG34",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__PANZER_III_AUSF_N(cls) -> "HLLWeapon":
        """*COAXIAL MG34 [Panzer III Ausf.N]*"""
        return cls(
            id="COAXIAL MG34 [Panzer III Ausf.N]",
            name="MG34",
            vehicle_id="Panzer III Ausf.N",
            factions={HLLFaction.DAK},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__SD_KFZ_121_LUCHS(cls) -> "HLLWeapon":
        """*COAXIAL MG34 [Sd.Kfz.121 Luchs]*"""
        return cls(
            id="COAXIAL MG34 [Sd.Kfz.121 Luchs]",
            name="MG34",
            vehicle_id="Sd.Kfz.121 Luchs",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__SD_KFZ_161_PANZER_IV(cls) -> "HLLWeapon":
        """*COAXIAL MG34 [Sd.Kfz.161 Panzer IV]*"""
        return cls(
            id="COAXIAL MG34 [Sd.Kfz.161 Panzer IV]",
            name="MG34",
            vehicle_id="Sd.Kfz.161 Panzer IV",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__SD_KFZ_171_PANTHER(cls) -> "HLLWeapon":
        """*COAXIAL MG34 [Sd.Kfz.171 Panther]*"""
        return cls(
            id="COAXIAL MG34 [Sd.Kfz.171 Panther]",
            name="MG34",
            vehicle_id="Sd.Kfz.171 Panther",
            factions={HLLFaction.GER},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__SD_KFZ_181_TIGER_1(cls) -> "HLLWeapon":
        """*COAXIAL MG34 [Sd.Kfz.181 Tiger 1]*"""
        return cls(
            id="COAXIAL MG34 [Sd.Kfz.181 Tiger 1]",
            name="MG34",
            vehicle_id="Sd.Kfz.181 Tiger 1",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_COAXIAL_MG34__SD_KFZ_234_PUMA(cls) -> "HLLWeapon":
        """*COAXIAL MG34 [Sd.Kfz.234 Puma]*"""
        return cls(
            id="COAXIAL MG34 [Sd.Kfz.234 Puma]",
            name="MG34",
            vehicle_id="Sd.Kfz.234 Puma",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__CHURCHILL_MK_III_A_V_R_E(cls) -> "HLLWeapon":
        """*Churchill Mk III A.V.R.E.*"""
        return cls(
            id="Churchill Mk III A.V.R.E.",
            name="Churchill Mk III A.V.R.E.",
            vehicle_id="Churchill Mk III A.V.R.E.",
            factions={HLLFaction.CW},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__CHURCHILL_MK_III(cls) -> "HLLWeapon":
        """*Churchill Mk.III*"""
        return cls(
            id="Churchill Mk.III",
            name="Churchill Mk.III",
            vehicle_id="Churchill Mk.III",
            factions={HLLFaction.B8A},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__CHURCHILL_MK_VII(cls) -> "HLLWeapon":
        """*Churchill Mk.VII*"""
        return cls(
            id="Churchill Mk.VII",
            name="Churchill Mk.VII",
            vehicle_id="Churchill Mk.VII",
            factions={HLLFaction.CW},
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__CRUSADER_MK_III(cls) -> "HLLWeapon":
        """*Crusader Mk.III*"""
        return cls(
            id="Crusader Mk.III",
            name="Crusader Mk.III",
            vehicle_id="Crusader Mk.III",
            factions={HLLFaction.B8A},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_D_5T_85MM__UNKNOWN(cls) -> "HLLWeapon":
        """*D-5T 85MM*"""
        return cls(
            id="D-5T 85MM",
            name="D-5T 85mm",
            vehicle_id=None,
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_D_5T_85MM__IS_1(cls) -> "HLLWeapon":
        """*D-5T 85MM [IS-1]*"""
        return cls(
            id="D-5T 85MM [IS-1]",
            name="D-5T 85mm",
            vehicle_id="IS-1",
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_CANNON,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_EXHAUST_FUEL_INJECTION__IS_1(cls) -> "HLLWeapon":
        """*Exhaust Fuel Injection [IS-1]*"""
        return cls(
            id="Exhaust Fuel Injection [IS-1]",
            name="Smoke Screen",
            vehicle_id="IS-1",
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_SMOKE_SCREEN,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_BESA__UNKNOWN(cls) -> "HLLWeapon":
        """*HULL BESA*"""
        return cls(
            id="HULL BESA",
            name="BESA",
            vehicle_id=None,
            factions={HLLFaction.CW},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_BESA_7_92MM__UNKNOWN(cls) -> "HLLWeapon":
        """*HULL BESA 7.92mm*"""
        return cls(
            id="HULL BESA 7.92mm",
            name="7.92mm",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_BESA_7_92MM__CHURCHILL_MK_III_A_V_R_E(cls) -> "HLLWeapon":
        """*HULL BESA 7.92mm [Churchill Mk III A.V.R.E.]*"""
        return cls(
            id="HULL BESA 7.92mm [Churchill Mk III A.V.R.E.]",
            name="BESA",
            vehicle_id="Churchill Mk III A.V.R.E.",
            factions={HLLFaction.CW},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_BESA_7_92MM__CHURCHILL_MK_III(cls) -> "HLLWeapon":
        """*HULL BESA 7.92mm [Churchill Mk.III]*"""
        return cls(
            id="HULL BESA 7.92mm [Churchill Mk.III]",
            name="BESA",
            vehicle_id="Churchill Mk.III",
            factions={HLLFaction.B8A},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_BESA_7_92MM__CHURCHILL_MK_VII(cls) -> "HLLWeapon":
        """*HULL BESA 7.92mm [Churchill Mk.VII]*"""
        return cls(
            id="HULL BESA 7.92mm [Churchill Mk.VII]",
            name="BESA",
            vehicle_id="Churchill Mk.VII",
            factions={HLLFaction.CW},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_BESA__CROMWELL(cls) -> "HLLWeapon":
        """*HULL BESA [Cromwell]*"""
        return cls(
            id="HULL BESA [Cromwell]",
            name="BESA",
            vehicle_id="Cromwell",
            factions={HLLFaction.CW},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
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
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_DT__IS_1(cls) -> "HLLWeapon":
        """*HULL DT [IS-1]*"""
        return cls(
            id="HULL DT [IS-1]",
            name="DT",
            vehicle_id="IS-1",
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_DT__KV_2(cls) -> "HLLWeapon":
        """*HULL DT [KV-2]*"""
        return cls(
            id="HULL DT [KV-2]",
            name="DT",
            vehicle_id="KV-2",
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_DT__T34_76(cls) -> "HLLWeapon":
        """*HULL DT [T34/76]*"""
        return cls(
            id="HULL DT [T34/76]",
            name="DT",
            vehicle_id="T34/76",
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__UNKNOWN(cls) -> "HLLWeapon":
        """*HULL M1919*"""
        return cls(
            id="HULL M1919",
            name="M1919 Browning",
            vehicle_id=None,
            factions={HLLFaction.US, HLLFaction.B8A},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__M3_STUART_HONEY(cls) -> "HLLWeapon":
        """*HULL M1919 [M3 Stuart Honey]*"""
        return cls(
            id="HULL M1919 [M3 Stuart Honey]",
            name="M1919 Browning",
            vehicle_id="M3 Stuart Honey",
            factions={HLLFaction.B8A},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__M4A3_105MM(cls) -> "HLLWeapon":
        """*HULL M1919 [M4A3 (105mm)]*"""
        return cls(
            id="HULL M1919 [M4A3 (105mm)]",
            name="M1919 Browning",
            vehicle_id="M4A3 (105mm)",
            factions={HLLFaction.US},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__SHERMAN_M4A375W(cls) -> "HLLWeapon":
        """*HULL M1919 [Sherman M4A3(75)W]*"""
        return cls(
            id="HULL M1919 [Sherman M4A3(75)W]",
            name="M1919 Browning",
            vehicle_id="Sherman M4A3(75)W",
            factions={HLLFaction.US},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__SHERMAN_M4A3E276(cls) -> "HLLWeapon":
        """*HULL M1919 [Sherman M4A3E2(76)]*"""
        return cls(
            id="HULL M1919 [Sherman M4A3E2(76)]",
            name="M1919 Browning",
            vehicle_id="Sherman M4A3E2(76)",
            factions={HLLFaction.US},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__SHERMAN_M4A3E2(cls) -> "HLLWeapon":
        """*HULL M1919 [Sherman M4A3E2]*"""
        return cls(
            id="HULL M1919 [Sherman M4A3E2]",
            name="M1919 Browning",
            vehicle_id="Sherman M4A3E2",
            factions={HLLFaction.US},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_M1919__STUART_M5A1(cls) -> "HLLWeapon":
        """*HULL M1919 [Stuart M5A1]*"""
        return cls(
            id="HULL M1919 [Stuart M5A1]",
            name="M1919 Browning",
            vehicle_id="Stuart M5A1",
            factions={HLLFaction.US},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_MG34__UNKNOWN(cls) -> "HLLWeapon":
        """*HULL MG34*"""
        return cls(
            id="HULL MG34",
            name="MG34",
            vehicle_id=None,
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_MG34__PANZER_III_AUSF_N(cls) -> "HLLWeapon":
        """*HULL MG34 [Panzer III Ausf.N]*"""
        return cls(
            id="HULL MG34 [Panzer III Ausf.N]",
            name="MG34",
            vehicle_id="Panzer III Ausf.N",
            factions={HLLFaction.DAK},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_MG34__SD_KFZ_161_PANZER_IV(cls) -> "HLLWeapon":
        """*HULL MG34 [Sd.Kfz.161 Panzer IV]*"""
        return cls(
            id="HULL MG34 [Sd.Kfz.161 Panzer IV]",
            name="MG34",
            vehicle_id="Sd.Kfz.161 Panzer IV",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_MG34__SD_KFZ_171_PANTHER(cls) -> "HLLWeapon":
        """*HULL MG34 [Sd.Kfz.171 Panther]*"""
        return cls(
            id="HULL MG34 [Sd.Kfz.171 Panther]",
            name="MG34",
            vehicle_id="Sd.Kfz.171 Panther",
            factions={HLLFaction.GER},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_HULL_MG34__SD_KFZ_181_TIGER_1(cls) -> "HLLWeapon":
        """*HULL MG34 [Sd.Kfz.181 Tiger 1]*"""
        return cls(
            id="HULL MG34 [Sd.Kfz.181 Tiger 1]",
            name="MG34",
            vehicle_id="Sd.Kfz.181 Tiger 1",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.TANK_HULL_MG,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.MOUNTED_MG,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_M6_37MM__UNKNOWN(cls) -> "HLLWeapon":
        """*M6 37mm*"""
        return cls(
            id="M6 37mm",
            name="37mm Cannon",
            vehicle_id=None,
            factions={HLLFaction.US},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_M6_37MM__M8_GREYHOUND(cls) -> "HLLWeapon":
        """*M6 37mm [M8 Greyhound]*"""
        return cls(
            id="M6 37mm [M8 Greyhound]",
            name="37mm Cannon",
            vehicle_id="M8 Greyhound",
            factions={HLLFaction.US},
            type=WeaponType.TANK_CANNON,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_MG_42__SD_KFZ_251_HALF_TRACK(cls) -> "HLLWeapon":
        """*MG 42 [Sd.Kfz 251 Half-track]*"""
        return cls(
            id="MG 42 [Sd.Kfz 251 Half-track]",
            name="MG42",
            vehicle_id="Sd.Kfz 251 Half-track",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.MOUNTED_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_OQF_57MM__UNKNOWN(cls) -> "HLLWeapon":
        """*OQF 57MM*"""
        return cls(
            id="OQF 57MM",
            name="QF 57mm",
            vehicle_id=None,
            factions={HLLFaction.B8A},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_OQF_57MM__CHURCHILL_MK_III(cls) -> "HLLWeapon":
        """*OQF 57MM [Churchill Mk.III]*"""
        return cls(
            id="OQF 57MM [Churchill Mk.III]",
            name="QF 57mm",
            vehicle_id="Churchill Mk.III",
            factions={HLLFaction.B8A},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_OQF_57MM__CRUSADER_MK_III(cls) -> "HLLWeapon":
        """*OQF 57MM [Crusader Mk.III]*"""
        return cls(
            id="OQF 57MM [Crusader Mk.III]",
            name="QF 57mm",
            vehicle_id="Crusader Mk.III",
            factions={HLLFaction.B8A},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_OQF_75MM__UNKNOWN(cls) -> "HLLWeapon":
        """*OQF 75MM*"""
        return cls(
            id="OQF 75MM",
            name="QF 75mm",
            vehicle_id=None,
            factions={HLLFaction.CW},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_OQF_75MM__CHURCHILL_MK_VII(cls) -> "HLLWeapon":
        """*OQF 75MM [Churchill Mk.VII]*"""
        return cls(
            id="OQF 75MM [Churchill Mk.VII]",
            name="QF 75mm",
            vehicle_id="Churchill Mk.VII",
            factions={HLLFaction.CW},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_OQF_75MM__CROMWELL(cls) -> "HLLWeapon":
        """*OQF 75MM [Cromwell]*"""
        return cls(
            id="OQF 75MM [Cromwell]",
            name="QF 75mm",
            vehicle_id="Cromwell",
            factions={HLLFaction.CW},
            type=WeaponType.TANK_CANNON,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_PRIMARY__BA_10(cls) -> "HLLWeapon":
        """*PRIMARY [BA-10]*"""
        return cls(
            id="PRIMARY [BA-10]",
            name="Receive Intel",
            vehicle_id="BA-10",
            factions={HLLFaction.SOV},
            type=WeaponType.TANK_RECON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_PRIMARY__DAIMLER(cls) -> "HLLWeapon":
        """*PRIMARY [Daimler]*"""
        return cls(
            id="PRIMARY [Daimler]",
            name="Receive Intel",
            vehicle_id="Daimler",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.TANK_RECON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_PRIMARY__M8_GREYHOUND(cls) -> "HLLWeapon":
        """*PRIMARY [M8 Greyhound]*"""
        return cls(
            id="PRIMARY [M8 Greyhound]",
            name="Receive Intel",
            vehicle_id="M8 Greyhound",
            factions={HLLFaction.US},
            type=WeaponType.TANK_RECON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_PRIMARY__SD_KFZ_234_PUMA(cls) -> "HLLWeapon":
        """*PRIMARY [Sd.Kfz.234 Puma]*"""
        return cls(
            id="PRIMARY [Sd.Kfz.234 Puma]",
            name="Receive Intel",
            vehicle_id="Sd.Kfz.234 Puma",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.TANK_RECON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__PANZER_III_AUSF_N(cls) -> "HLLWeapon":
        """*Panzer III Ausf.N*"""
        return cls(
            id="Panzer III Ausf.N",
            name="Panzer III Ausf.N",
            vehicle_id="Panzer III Ausf.N",
            factions={HLLFaction.DAK},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_QF_17_POUNDER__UNKNOWN(cls) -> "HLLWeapon":
        """*QF 17-POUNDER*"""
        return cls(
            id="QF 17-POUNDER",
            name="QF 17-Pounder",
            vehicle_id=None,
            factions={HLLFaction.CW},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_QF_17_POUNDER__FIREFLY(cls) -> "HLLWeapon":
        """*QF 17-POUNDER [Firefly]*"""
        return cls(
            id="QF 17-POUNDER [Firefly]",
            name="QF 17-Pounder",
            vehicle_id="Firefly",
            factions={HLLFaction.CW},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_QF_2_POUNDER__UNKNOWN(cls) -> "HLLWeapon":
        """*QF 2-POUNDER*"""
        return cls(
            id="QF 2-POUNDER",
            name="QF 2-Pounder",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_QF_2_POUNDER__DAIMLER(cls) -> "HLLWeapon":
        """*QF 2-POUNDER [Daimler]*"""
        return cls(
            id="QF 2-POUNDER [Daimler]",
            name="QF 2-Pounder",
            vehicle_id="Daimler",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_QF_2_POUNDER__TETRARCH(cls) -> "HLLWeapon":
        """*QF 2-POUNDER [Tetrarch]*"""
        return cls(
            id="QF 2-POUNDER [Tetrarch]",
            name="QF 2-Pounder",
            vehicle_id="Tetrarch",
            factions={HLLFaction.CW},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_QF_25_POUNDER__UNKNOWN_2(cls) -> "HLLWeapon":
        """*QF 25 POUNDER*"""
        return cls(
            id="QF 25 POUNDER",
            name="88mm Howitzer",
            vehicle_id=None,
            factions={HLLFaction.B8A},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_QF_25_POUNDER__BISHOP_SP_25PDR(cls) -> "HLLWeapon":
        """*QF 25 POUNDER [Bishop SP 25pdr]*"""
        return cls(
            id="QF 25 POUNDER [Bishop SP 25pdr]",
            name="88mm Howitzer",
            vehicle_id="Bishop SP 25pdr",
            factions={HLLFaction.B8A},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_QF_25_POUNDER__UNKNOWN(cls) -> "HLLWeapon":
        """*QF 25-POUNDER*"""
        return cls(
            id="QF 25-POUNDER",
            name="88mm Howitzer",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.ARTILLERY,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_QF_25_POUNDER__QF_25_POUNDER(cls) -> "HLLWeapon":
        """*QF 25-POUNDER [QF 25-Pounder]*"""
        return cls(
            id="QF 25-POUNDER [QF 25-Pounder]",
            name="88mm Howitzer",
            vehicle_id="QF 25-Pounder",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.ARTILLERY,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_QF_6_POUNDER__UNKNOWN(cls) -> "HLLWeapon":
        """*QF 6-POUNDER*"""
        return cls(
            id="QF 6-POUNDER",
            name="57mm Cannon",
            vehicle_id=None,
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.AT_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_QF_6_POUNDER__QF_6_POUNDER(cls) -> "HLLWeapon":
        """*QF 6-POUNDER [QF 6-Pounder]*"""
        return cls(
            id="QF 6-POUNDER [QF 6-Pounder]",
            name="57mm Cannon",
            vehicle_id="QF 6-Pounder",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=WeaponType.AT_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SD_KFZ_251_HALF_TRACK(cls) -> "HLLWeapon":
        """*Sd.Kfz 251 Half-track*"""
        return cls(
            id="Sd.Kfz 251 Half-track",
            name="Sd.Kfz 251 Half-track",
            vehicle_id="Sd.Kfz 251 Half-track",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SD_KFZ_121_LUCHS(cls) -> "HLLWeapon":
        """*Sd.Kfz.121 Luchs*"""
        return cls(
            id="Sd.Kfz.121 Luchs",
            name="Sd.Kfz.121 Luchs",
            vehicle_id="Sd.Kfz.121 Luchs",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SD_KFZ_161_PANZER_IV(cls) -> "HLLWeapon":
        """*Sd.Kfz.161 Panzer IV*"""
        return cls(
            id="Sd.Kfz.161 Panzer IV",
            name="Sd.Kfz.161 Panzer IV",
            vehicle_id="Sd.Kfz.161 Panzer IV",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SD_KFZ_171_PANTHER(cls) -> "HLLWeapon":
        """*Sd.Kfz.171 Panther*"""
        return cls(
            id="Sd.Kfz.171 Panther",
            name="Sd.Kfz.171 Panther",
            vehicle_id="Sd.Kfz.171 Panther",
            factions={HLLFaction.GER},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SD_KFZ_181_TIGER_1(cls) -> "HLLWeapon":
        """*Sd.Kfz.181 Tiger 1*"""
        return cls(
            id="Sd.Kfz.181 Tiger 1",
            name="Sd.Kfz.181 Tiger 1",
            vehicle_id="Sd.Kfz.181 Tiger 1",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SD_KFZ_234_PUMA(cls) -> "HLLWeapon":
        """*Sd.Kfz.234 Puma*"""
        return cls(
            id="Sd.Kfz.234 Puma",
            name="Sd.Kfz.234 Puma",
            vehicle_id="Sd.Kfz.234 Puma",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.TANK_CANNON,
            magnification=None,
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
            type=WeaponType.TANK_CANNON,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.ROADKILL,
            magnification=None,
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
            type=WeaponType.UNKNOWN,
        )

    @class_cached_property
    @classmethod
    def BOMBING_RUN(cls) -> "HLLWeapon":
        """*BOMBING RUN*"""
        return cls(
            id="BOMBING RUN",
            name="Bombing Run",
            factions=set(HLLFaction.all()) - {HLLFaction.SOV},
            type=WeaponType.COMMANDER_ABILITY,
        )

    @class_cached_property
    @classmethod
    def STRAFING_RUN(cls) -> "HLLWeapon":
        """*STRAFING RUN*"""
        return cls(
            id="STRAFING RUN",
            name="Strafing Run",
            factions=set(HLLFaction.all()),
            type=WeaponType.COMMANDER_ABILITY,
        )

    @class_cached_property
    @classmethod
    def PRECISION_STRIKE(cls) -> "HLLWeapon":
        """*PRECISION STRIKE*"""
        return cls(
            id="PRECISION STRIKE",
            name="Precision Strike",
            factions=set(HLLFaction.all()),
            type=WeaponType.COMMANDER_ABILITY,
        )

    @class_cached_property
    @classmethod
    def ARTILLERY_STRIKE(cls) -> "HLLWeapon":
        """*Unknown*"""
        return cls(
            id="Unknown",
            name="Artillery Strike",
            factions=set(HLLFaction.all()),
            type=WeaponType.COMMANDER_ABILITY,
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
            type=WeaponType.UNKNOWN,
        )


class HLLVWeapon(_Weapon[HLLVFaction, "HLLVVehicle"]):
    # @computed_field(repr=False)
    @cached_property
    def vehicle(self) -> "HLLVVehicle | None":
        from hllrcon.data.vehicles import HLLVVehicle  # noqa: PLC0415

        if self.vehicle_id:
            return HLLVVehicle.by_id(self.vehicle_id)
        return None

    ### INJECT "hllv loadout items" START

    @class_cached_property
    @classmethod
    def AMMO_BOX(cls) -> "HLLVWeapon":
        """*Ammo Box*"""
        return cls(
            id="Ammo Box",
            name="Small Ammo Box",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.SUPPLIES,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def ANTI_AIRCRAFT_GUN_WRENCH(cls) -> "HLLVWeapon":
        """*Anti-Aircraft Gun Wrench*"""
        return cls(
            id="Anti-Aircraft Gun Wrench",
            name="Wrench",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.WRENCH,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def AN_M8_FLARE(cls) -> "HLLVWeapon":
        """*AN-M8 Flare*"""
        return cls(
            id="AN-M8 Flare",
            name="AN-M8 Flare Pistol",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.RECON_FLARE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def BANDAGE_NVA(cls) -> "HLLVWeapon":
        """*Bandage*"""
        return cls(
            id="Bandage",
            name="Bandage",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.HEALING,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def BANDAGE_US(cls) -> "HLLVWeapon":
        """*BANDAGE*"""
        return cls(
            id="BANDAGE",
            name="Bandage",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.HEALING,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def BINOCULARS(cls) -> "HLLVWeapon":
        """*Binoculars*"""
        return cls(
            id="Binoculars",
            name="Binoculars",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.BINOCULARS,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def BLOW_TORCH(cls) -> "HLLVWeapon":
        """*BLOW TORCH*"""
        return cls(
            id="BLOW TORCH",
            name="Blowtorch",
            vehicle_id=None,
            factions={HLLVFaction.US, HLLVFaction.NVA},
            type=WeaponType.TORCH,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def CHI_COM_SIGNAL_PISTOL(cls) -> "HLLVWeapon":
        """*Chi Com Signal Pistol*"""
        return cls(
            id="Chi Com Signal Pistol",
            name="Chi-Com Flare Pistol",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.RECON_FLARE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def DH10_AP_MINE(cls) -> "HLLVWeapon":
        """*DH10 AP Mine*"""
        return cls(
            id="DH10 AP Mine",
            name="DH-10 AP Mine",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.AP_MINE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def EXPLOSIVE_AMMO_BOX(cls) -> "HLLVWeapon":
        """*Explosive Ammo Box*"""
        return cls(
            id="Explosive Ammo Box",
            name="Explosive Ammo Box",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.SUPPLIES,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def FIELD_PAD(cls) -> "HLLVWeapon":
        """*FIELD PAD*"""
        return cls(
            id="FIELD PAD",
            name="Field Pad",
            vehicle_id=None,
            factions={HLLVFaction.US, HLLVFaction.NVA},
            type=WeaponType.WATCH,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def HAMMER(cls) -> "HLLVWeapon":
        """*Hammer*"""
        return cls(
            id="Hammer",
            name="Hammer",
            vehicle_id=None,
            factions={HLLVFaction.US, HLLVFaction.NVA},
            type=WeaponType.HAMMER,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def HE_AMMO_BOX(cls) -> "HLLVWeapon":
        """*HE Ammo Box*"""
        return cls(
            id="HE Ammo Box",
            name="Explosive Ammo Box",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.SUPPLIES,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def IZH_58(cls) -> "HLLVWeapon":
        """*IZH 58*"""
        return cls(
            id="IZH 58",
            name="IZh-58",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.SHOTGUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def K50M(cls) -> "HLLVWeapon":
        """*K50M*"""
        return cls(
            id="K50M",
            name="K-50M",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.SUBMACHINE_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def K50M_DRUM(cls) -> "HLLVWeapon":
        """*K50M Drum*"""
        return cls(
            id="K50M Drum",
            name="K-50M w/Drum",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.SUBMACHINE_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def KNIFE(cls) -> "HLLVWeapon":
        """*Knife*"""
        return cls(
            id="Knife",
            name="Knife",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.MELEE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def LIGHT_MORTAR(cls) -> "HLLVWeapon":
        """*Light Mortar*"""
        return cls(
            id="Light Mortar",
            name="Wrench",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.WRENCH,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def LPO_50(cls) -> "HLLVWeapon":
        """*LPO-50*"""
        return cls(
            id="LPO-50",
            name="LPO-50 Flamethrower",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.FLAMETHROWER,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M16A1(cls) -> "HLLVWeapon":
        """*M16A1*"""
        return cls(
            id="M16A1",
            name="M16A1",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.ASSAULT_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M16A1_M203(cls) -> "HLLVWeapon":
        """*M16A1-M203*"""
        return cls(
            id="M16A1-M203",
            name="M16A1 w/M203",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.ASSAULT_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M16A1_WITH_BAYONET(cls) -> "HLLVWeapon":
        """*M16A1 With Bayonet*"""
        return cls(
            id="M16A1 With Bayonet",
            name="M16A1 w/Bayonet",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.ASSAULT_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M183_DEMOLITION_CHARGE(cls) -> "HLLVWeapon":
        """*M183 Demolition Charge*"""
        return cls(
            id="M183 Demolition Charge",
            name="M183 Demolition Charge",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.SATCHEL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M18_CLAYMORE(cls) -> "HLLVWeapon":
        """*M18 Claymore*"""
        return cls(
            id="M18 Claymore",
            name="M18 Claymore",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.AP_MINE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M18_SMOKE_GRENADE(cls) -> "HLLVWeapon":
        """*M18 Smoke Grenade*"""
        return cls(
            id="M18 Smoke Grenade",
            name="M18 Smoke Grenade",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.SMOKE_GRENADE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M1911A1(cls) -> "HLLVWeapon":
        """*M1911A1*"""
        return cls(
            id="M1911A1",
            name="M1911A1",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.PISTOL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M21_AT_MINE(cls) -> "HLLVWeapon":
        """*M21 AT Mine*"""
        return cls(
            id="M21 AT Mine",
            name="M21 AT Mine",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.AT_MINE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M2A1_7(cls) -> "HLLVWeapon":
        """*M2A1-7*"""
        return cls(
            id="M2A1-7",
            name="M2 Flamethrower",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.FLAMETHROWER,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M3_BINOCULARS(cls) -> "HLLVWeapon":
        """*M3 Binoculars*"""
        return cls(
            id="M3 Binoculars",
            name="M3 Binoculars",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.BINOCULARS,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M3_KNIFE(cls) -> "HLLVWeapon":
        """*M3 Knife*"""
        return cls(
            id="M3 Knife",
            name="M3 Knife",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.MELEE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M40(cls) -> "HLLVWeapon":
        """*M40*"""
        return cls(
            id="M40",
            name="M40",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=4,
        )

    @class_cached_property
    @classmethod
    def M60(cls) -> "HLLVWeapon":
        """*M60*"""
        return cls(
            id="M60",
            name="M60",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.MACHINE_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M61_FRAG_GRENADE(cls) -> "HLLVWeapon":
        """*M61 Frag Grenade*"""
        return cls(
            id="M61 Frag Grenade",
            name="M61 Grenade",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.GRENADE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M72(cls) -> "HLLVWeapon":
        """*M72 *"""
        return cls(
            id="M72 ",
            name="M72 LAW",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.ROCKET_LAUNCHER,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def M79(cls) -> "HLLVWeapon":
        """*M79 *"""
        return cls(
            id="M79 ",
            name="M79 Grenade Launcher",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.GRENADE_LAUNCHER,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def MEDICAL_SUPPLIES(cls) -> "HLLVWeapon":
        """*Medical Supplies*"""
        return cls(
            id="Medical Supplies",
            name="Medical Supplies",
            vehicle_id=None,
            factions={HLLVFaction.US, HLLVFaction.NVA},
            type=WeaponType.SUPPLIES,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def MODEL_77E(cls) -> "HLLVWeapon":
        """*Model 77E*"""
        return cls(
            id="Model 77E",
            name="Model 77E",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.SHOTGUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def RDG_1(cls) -> "HLLVWeapon":
        """*RDG-1*"""
        return cls(
            id="RDG-1",
            name="RDG-1 Smoke Grenade",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.SMOKE_GRENADE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def REVIVE_NVA(cls) -> "HLLVWeapon":
        """*Revive*"""
        return cls(
            id="Revive",
            name="Revive",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.HEALING,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def REVIVE_US(cls) -> "HLLVWeapon":
        """*REVIVE*"""
        return cls(
            id="REVIVE",
            name="Revive",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.HEALING,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def RPD(cls) -> "HLLVWeapon":
        """*RPD*"""
        return cls(
            id="RPD",
            name="RPD",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.MACHINE_GUN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def RPG_02(cls) -> "HLLVWeapon":
        """*RPG-02*"""
        return cls(
            id="RPG-02",
            name="RPG-02",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.ROCKET_LAUNCHER,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def SATCHEL_CHARGE(cls) -> "HLLVWeapon":
        """*Satchel Charge*"""
        return cls(
            id="Satchel Charge",
            name="Satchel Charge",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.SATCHEL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def SMALL_AMMUNITION_BOX(cls) -> "HLLVWeapon":
        """*Small Ammunition Box*"""
        return cls(
            id="Small Ammunition Box",
            name="Small Ammo Box",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.SUPPLIES,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def SUPPLIES(cls) -> "HLLVWeapon":
        """*Supplies*"""
        return cls(
            id="Supplies",
            name="Supplies",
            vehicle_id=None,
            factions={HLLVFaction.US, HLLVFaction.NVA},
            type=WeaponType.SUPPLIES,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def TM_46_AT_MINE(cls) -> "HLLVWeapon":
        """*TM-46 AT Mine*"""
        return cls(
            id="TM-46 AT Mine",
            name="TM-46 AT Mine",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.AT_MINE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def TNT(cls) -> "HLLVWeapon":
        """*TNT*"""
        return cls(
            id="TNT",
            name="TNT",
            vehicle_id=None,
            factions={HLLVFaction.US},
            type=WeaponType.SATCHEL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def TYPE_53(cls) -> "HLLVWeapon":
        """*Type 53*"""
        return cls(
            id="Type 53",
            name="Type 53",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def TYPE_53_PU(cls) -> "HLLVWeapon":
        """*Type 53 PU*"""
        return cls(
            id="Type 53 PU",
            name="Type 53",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=4,
        )

    @class_cached_property
    @classmethod
    def TYPE_53_W_N4_RIFLE_LAUNCHER(cls) -> "HLLVWeapon":
        """*Type 53 W/ N4 Rifle Launcher*"""
        return cls(
            id="Type 53 W/ N4 Rifle Launcher",
            name="Type 53 w/N4",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.BOLT_ACTION_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def TYPE_54(cls) -> "HLLVWeapon":
        """*Type 54*"""
        return cls(
            id="Type 54",
            name="Type 54",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.PISTOL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def TYPE_56_W_BAYONET(cls) -> "HLLVWeapon":
        """*Type 56 W/ Bayonet*"""
        return cls(
            id="Type 56 W/ Bayonet",
            name="Type 56 w/Bayonet",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.ASSAULT_RIFLE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def TYPE_67(cls) -> "HLLVWeapon":
        """*Type 67*"""
        return cls(
            id="Type 67",
            name="Type 67 Grenade",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.GRENADE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def WRENCH(cls) -> "HLLVWeapon":
        """*Wrench*"""
        return cls(
            id="Wrench",
            name="Wrench",
            vehicle_id=None,
            factions={HLLVFaction.US, HLLVFaction.NVA},
            type=WeaponType.WRENCH,
            magnification=None,
        )

    ### INJECT "hllv loadout items" END

    ### INJECT "hllv vehicles" START

    @class_cached_property
    @classmethod
    def V_100MM_D_10T_CANNON__UNKNOWN(cls) -> "HLLVWeapon":
        """*100MM D-10T CANNON*"""
        return cls(
            id="100MM D-10T CANNON",
            name="100MM D-10T CANNON",
            vehicle_id=None,
            factions={HLLVFaction.US, HLLVFaction.NVA},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_100MM_D_10T_CANNON__SD_KFZ_171_PANTHER(cls) -> "HLLVWeapon":
        """*100MM D-10T CANNON [Sd.Kfz.171 Panther]*"""
        return cls(
            id="100MM D-10T CANNON [Sd.Kfz.171 Panther]",
            name="100mm D-10T",
            vehicle_id="Sd.Kfz.171 Panther",
            factions={HLLVFaction.US, HLLVFaction.NVA},
            type=WeaponType.TANK_CANNON,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_DSHKM_ANTI_AIRCRAFT_GUN__UNKNOWN(cls) -> "HLLVWeapon":
        """*DShKM Anti-Aircraft Gun*"""
        return cls(
            id="DShKM Anti-Aircraft Gun",
            name="DShK",
            vehicle_id=None,
            factions={HLLVFaction.NVA},
            type=WeaponType.MOUNTED_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_DSHKM_ANTI_AIRCRAFT_GUN__DSHKM_ANTI_AIRCRAFT_GUN(cls) -> "HLLVWeapon":
        """*DShKM Anti-Aircraft Gun [DShKM Anti-Aircraft Gun]*"""
        return cls(
            id="DShKM Anti-Aircraft Gun [DShKM Anti-Aircraft Gun]",
            name="DShK",
            vehicle_id="DShKM Anti-Aircraft Gun",
            factions={HLLVFaction.NVA},
            type=WeaponType.MOUNTED_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_DHSK__NVA_BOAT(cls) -> "HLLVWeapon":
        """*Dhsk [NVA Boat]*"""
        return cls(
            id="Dhsk [NVA Boat]",
            name="DShK",
            vehicle_id="NVA Boat",
            factions={HLLVFaction.NVA},
            type=WeaponType.MOUNTED_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_FLARE_GUN__US_TRANSPORT_HELICOPTER(cls) -> "HLLVWeapon":
        """*Flare Gun [US Transport Helicopter]*"""
        return cls(
            id="Flare Gun [US Transport Helicopter]",
            name="Flare Gun",
            vehicle_id="US Transport Helicopter",
            factions={HLLVFaction.US},
            type=WeaponType.RECON_FLARE,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__GAZ_63_SUPPLY(cls) -> "HLLVWeapon":
        """*Gaz 63 (Supply)*"""
        return cls(
            id="Gaz 63 (Supply)",
            name="Gaz 63 (Supply)",
            vehicle_id="Gaz 63 (Supply)",
            factions={HLLVFaction.NVA},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__GAZ_63_TRANSPORT(cls) -> "HLLVWeapon":
        """*Gaz 63 (Transport)*"""
        return cls(
            id="Gaz 63 (Transport)",
            name="Gaz 63 (Transport)",
            vehicle_id="Gaz 63 (Transport)",
            factions={HLLVFaction.NVA},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_M2_BROWNING__US_BOAT(cls) -> "HLLVWeapon":
        """*M2 Browning [US Boat]*"""
        return cls(
            id="M2 Browning [US Boat]",
            name="M2 Browning",
            vehicle_id="US Boat",
            factions={HLLVFaction.US},
            type=WeaponType.MOUNTED_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__M35_SUPPLY(cls) -> "HLLVWeapon":
        """*M35 (Supply)*"""
        return cls(
            id="M35 (Supply)",
            name="M35 (Supply)",
            vehicle_id="M35 (Supply)",
            factions={HLLVFaction.US},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__M35_TRANSPORT(cls) -> "HLLVWeapon":
        """*M35 (Transport)*"""
        return cls(
            id="M35 (Transport)",
            name="M35 (Transport)",
            vehicle_id="M35 (Transport)",
            factions={HLLVFaction.US},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_M60D__US_TRANSPORT_HELICOPTER(cls) -> "HLLVWeapon":
        """*M60D [US Transport Helicopter]*"""
        return cls(
            id="M60D [US Transport Helicopter]",
            name="M60D",
            vehicle_id="US Transport Helicopter",
            factions={HLLVFaction.US},
            type=WeaponType.MOUNTED_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_MORTAR__UNKNOWN(cls) -> "HLLVWeapon":
        """*MORTAR*"""
        return cls(
            id="MORTAR",
            name="Mortar",
            vehicle_id=None,
            factions={HLLVFaction.US, HLLVFaction.NVA},
            type=WeaponType.MORTAR,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_MORTAR__MORTAR(cls) -> "HLLVWeapon":
        """*MORTAR [MORTAR]*"""
        return cls(
            id="MORTAR [MORTAR]",
            name="Mortar",
            vehicle_id="MORTAR",
            factions={HLLVFaction.US, HLLVFaction.NVA},
            type=WeaponType.MORTAR,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__NVA_BOAT(cls) -> "HLLVWeapon":
        """*NVA Boat*"""
        return cls(
            id="NVA Boat",
            name="NVA Boat",
            vehicle_id="NVA Boat",
            factions={HLLVFaction.NVA},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_NONE__SD_KFZ_171_PANTHER(cls) -> "HLLVWeapon":
        """*None [Sd.Kfz.171 Panther]*"""
        return cls(
            id="None [Sd.Kfz.171 Panther]",
            name="Smoke Screen",
            vehicle_id="Sd.Kfz.171 Panther",
            factions={HLLVFaction.US, HLLVFaction.NVA},
            type=WeaponType.TANK_SMOKE_SCREEN,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_RPD__NVA_BOAT(cls) -> "HLLVWeapon":
        """*RPD [NVA Boat]*"""
        return cls(
            id="RPD [NVA Boat]",
            name="RPD",
            vehicle_id="NVA Boat",
            factions={HLLVFaction.NVA},
            type=WeaponType.MOUNTED_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_SGMT_7_62MM__UNKNOWN(cls) -> "HLLVWeapon":
        """*SGMT 7.62MM*"""
        return cls(
            id="SGMT 7.62MM",
            name="SGMT",
            vehicle_id=None,
            factions={HLLVFaction.US, HLLVFaction.NVA},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_SGMT_7_62MM__SD_KFZ_171_PANTHER(cls) -> "HLLVWeapon":
        """*SGMT 7.62MM [Sd.Kfz.171 Panther]*"""
        return cls(
            id="SGMT 7.62MM [Sd.Kfz.171 Panther]",
            name="SGMT",
            vehicle_id="Sd.Kfz.171 Panther",
            factions={HLLVFaction.US, HLLVFaction.NVA},
            type=WeaponType.TANK_COAXIAL_MG,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__SD_KFZ_171_PANTHER(cls) -> "HLLVWeapon":
        """*Sd.Kfz.171 Panther*"""
        return cls(
            id="Sd.Kfz.171 Panther",
            name="Sd.Kfz.171 Panther",
            vehicle_id="Sd.Kfz.171 Panther",
            factions={HLLVFaction.US, HLLVFaction.NVA},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__US_BOAT(cls) -> "HLLVWeapon":
        """*US Boat*"""
        return cls(
            id="US Boat",
            name="US Boat",
            vehicle_id="US Boat",
            factions={HLLVFaction.US},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__US_SUPPLY_HELICOPTER(cls) -> "HLLVWeapon":
        """*US Supply Helicopter*"""
        return cls(
            id="US Supply Helicopter",
            name="US Supply Helicopter",
            vehicle_id="US Supply Helicopter",
            factions={HLLVFaction.US},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    @class_cached_property
    @classmethod
    def V_ROADKILL__US_TRANSPORT_HELICOPTER(cls) -> "HLLVWeapon":
        """*US Transport Helicopter*"""
        return cls(
            id="US Transport Helicopter",
            name="US Transport Helicopter",
            vehicle_id="US Transport Helicopter",
            factions={HLLVFaction.US},
            type=WeaponType.ROADKILL,
            magnification=None,
        )

    ### INJECT "hllv vehicles" END


AnyWeapon: TypeAlias = HLLWeapon | HLLVWeapon
