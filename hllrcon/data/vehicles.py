# ruff: noqa: N802, D400, D415
from enum import StrEnum
from typing import Annotated, Generic, TypeAlias, TypeVar

from pydantic import BaseModel, Field

from hllrcon.data._utils import (
    IndexedBaseModel,
    class_cached_property,
    model_sequence_serializer,
)
from hllrcon.data.factions import HLLFaction, HLLVFaction, _Faction
from hllrcon.data.roles import (
    HLLRole,
    HLLRoleType,
    HLLVRole,
    HLLVRoleType,
    _Role,
)
from hllrcon.data.weapons import HLLVWeapon, HLLWeapon, _Weapon

_HLL_TANK_CREW_ROLES = {
    role for role in HLLRole.all() if role.type == HLLRoleType.ARMOR
}
_HLL_ARTY_CREW_ROLES = {
    role for role in HLLRole.all() if role.type == HLLRoleType.ARTILLERY
}
_HLLV_TANK_CREW_ROLES = {
    role for role in HLLVRole.all() if role.type == HLLVRoleType.ARMOR
}
_HLLV_MORTAR_CREW_ROLES = {
    role for role in HLLVRole.all() if role.type == HLLVRoleType.MORTAR
}


FactionT = TypeVar("FactionT", bound=_Faction)
VehicleSeatT = TypeVar("VehicleSeatT", bound="_VehicleSeat")
VehicleSeatTypeT = TypeVar("VehicleSeatTypeT", bound="_VehicleSeatType")
VehicleTypeT = TypeVar("VehicleTypeT", bound="_VehicleType")
WeaponT = TypeVar("WeaponT", bound=_Weapon)
RoleT = TypeVar("RoleT", bound=_Role)


class _VehicleType(StrEnum):
    pass


class HLLVehicleType(_VehicleType):
    HEAVY_TANK = "Heavy Tank"
    MEDIUM_TANK = "Medium Tank"
    LIGHT_TANK = "Light Tank"
    RECON_VEHICLE = "Recon Vehicle"
    HALF_TRACK = "Half-Track"
    TRANSPORT_TRUCK = "Transport Truck"
    SUPPLY_TRUCK = "Supply Truck"
    JEEP = "Jeep"
    SELF_PROPELLED_ARTILLERY = "Self-Propelled Artillery"
    ARTILLERY = "Artillery"
    ANTI_TANK_GUN = "Anti-Tank Gun"


class HLLVVehicleType(_VehicleType):
    pass


VehicleType: TypeAlias = HLLVehicleType | HLLVVehicleType


class _VehicleSeatType(StrEnum):
    pass


class HLLVehicleSeatType(_VehicleSeatType):
    DRIVER = "Driver"
    GUNNER = "Gunner"
    SPOTTER = "Spotter"
    LOADER = "Loader"
    PASSENGER = "Passenger"


class HLLVVehicleSeatType(_VehicleSeatType):
    pass


VehicleSeatType: TypeAlias = HLLVehicleSeatType | HLLVVehicleSeatType


class _VehicleSeat(BaseModel, Generic[RoleT, WeaponT, VehicleSeatTypeT], frozen=True):
    index: int
    type: VehicleSeatTypeT
    weapons: Annotated[
        list[WeaponT],
        Field(default_factory=list),
        model_sequence_serializer(str),
    ]
    requires_roles: Annotated[
        set[RoleT] | None,
        model_sequence_serializer(int, optional=True),
    ] = None
    exposed: bool


class HLLVehicleSeat(_VehicleSeat[HLLRole, HLLWeapon, HLLVehicleSeatType], frozen=True):
    pass


class HLLVVehicleSeat(
    _VehicleSeat[HLLVRole, HLLVWeapon, HLLVVehicleSeatType],
    frozen=True,
):
    pass


VehicleSeat: TypeAlias = HLLVehicleSeat | HLLVVehicleSeat


class _Vehicle(IndexedBaseModel[str], Generic[FactionT, VehicleSeatT, VehicleTypeT]):
    id: str
    name: str
    factions: Annotated[
        set[FactionT],
        Field(min_length=1),
        model_sequence_serializer(int),
    ]
    type: VehicleTypeT
    seats: list[VehicleSeatT]

    @property
    def is_truck(self) -> bool:
        """Whether the vehicle is a truck.

        Vehicle types included are:
        - Transport Truck
        - Supply Truck
        """
        return self.type in {
            HLLVehicleType.TRANSPORT_TRUCK,
            HLLVehicleType.SUPPLY_TRUCK,
        }

    @property
    def is_tank(self) -> bool:
        """Whether the vehicle is a tank.

        Tanks are vehicles that are exclusively operated by armor units.

        Vehicle types included are:
        - Heavy Tank
        - Medium Tank
        - Light Tank
        - Recon Vehicle
        """
        return self.type in {
            HLLVehicleType.HEAVY_TANK,
            HLLVehicleType.MEDIUM_TANK,
            HLLVehicleType.LIGHT_TANK,
            HLLVehicleType.RECON_VEHICLE,
        }

    @property
    def is_artillery(self) -> bool:
        """Whether the vehicle is an artillery piece.

        Artillery vehicles are exclusively operated by artillery units.

        Vehicle types included are:
        - Artillery
        - Self-Propelled Artillery
        """
        return self.type in {
            HLLVehicleType.SELF_PROPELLED_ARTILLERY,
            HLLVehicleType.ARTILLERY,
        }

    @property
    def is_emplacement(self) -> bool:
        """Whether the vehicle is an emplacement.

        Emplacements are static and cannot be driven around.

        Vehicle types included are:
        - Artillery
        - Anti-Tank Gun
        """
        return self.type in {
            HLLVehicleType.ARTILLERY,
            HLLVehicleType.ANTI_TANK_GUN,
        }


class HLLVehicle(_Vehicle[HLLFaction, HLLVehicleSeat, HLLVehicleType]):
    @class_cached_property
    @classmethod
    def M1_57MM(cls) -> "HLLVehicle":
        """*M1 57mm*"""
        return cls(
            id="M1 57mm",
            name="M1 57mm",
            type=HLLVehicleType.ANTI_TANK_GUN,
            factions={HLLFaction.US},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[HLLWeapon.V_57MM_CANNON__M1_57],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.LOADER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def M114(cls) -> "HLLVehicle":
        """*M114*"""
        return cls(
            id="M114",
            name="M114 Howitzer",
            type=HLLVehicleType.ARTILLERY,
            factions={HLLFaction.US},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[HLLWeapon.V_57MM_CANNON__M1_57],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.LOADER,
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def M8_GREYHOUND(cls) -> "HLLVehicle":
        """*M8 Greyhound*"""
        return cls(
            id="M8 Greyhound",
            name="M8 Greyhound",
            type=HLLVehicleType.RECON_VEHICLE,
            factions={HLLFaction.US},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_M6_37MM__M8_GREYHOUND,
                        HLLWeapon.V_COAXIAL_M1919__M8_GREYHOUND,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=4,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def STUART_M5A1(cls) -> "HLLVehicle":
        """*Stuart M5A1*"""
        return cls(
            id="Stuart M5A1",
            name="M5A1 Stuart",
            type=HLLVehicleType.LIGHT_TANK,
            factions={HLLFaction.US},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[
                        HLLWeapon.V_HULL_M1919__STUART_M5A1,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_37MM_CANNON__STUART_M5A1,
                        HLLWeapon.V_COAXIAL_M1919__STUART_M5A1,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SHERMAN_M4A3_75W(cls) -> "HLLVehicle":
        """*Sherman M4A3(75)W*"""
        return cls(
            id="Sherman M4A3(75)W",
            name="M4A3(75)W Sherman",
            type=HLLVehicleType.MEDIUM_TANK,
            factions={HLLFaction.US},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[
                        HLLWeapon.V_HULL_M1919__SHERMAN_M4A3_75W,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_HULL_M1919__SHERMAN_M4A3_75W,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SHERMAN_M4A3E2(cls) -> "HLLVehicle":
        """*Sherman M4A3E2*"""
        return cls(
            id="Sherman M4A3E2",
            name="M4A3E2 Sherman",
            type=HLLVehicleType.HEAVY_TANK,
            factions={HLLFaction.US},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[
                        HLLWeapon.V_HULL_M1919__SHERMAN_M4A3E2,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_75MM_M3_GUN__SHERMAN_M4A3E2,
                        HLLWeapon.V_COAXIAL_M1919__SHERMAN_M4A3E2,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SHERMAN_M4A3E2_76(cls) -> "HLLVehicle":
        """*Sherman M4A3E2(76)*"""
        return cls(
            id="Sherman M4A3E2(76)",
            name="M4A3E2(76) Sherman",
            type=HLLVehicleType.HEAVY_TANK,
            factions={HLLFaction.US},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[
                        HLLWeapon.V_HULL_M1919__SHERMAN_M4A3E2_76,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_76MM_M1_GUN__SHERMAN_M4A3E2_76,
                        HLLWeapon.V_COAXIAL_M1919__SHERMAN_M4A3E2_76,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def GMC_CCKW_353_SUPPLY(cls) -> "HLLVehicle":
        """*GMC CCKW 353 (Supply)*"""
        return cls(
            id="GMC CCKW 353 (Supply)",
            name="GMC CCKW 353",
            type=HLLVehicleType.SUPPLY_TRUCK,
            factions={HLLFaction.US},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def GMC_CCKW_353_TRANSPORT(cls) -> "HLLVehicle":
        """*GMC CCKW 353 (Transport)*"""
        return cls(
            id="GMC CCKW 353 (Transport)",
            name="GMC CCKW 353",
            type=HLLVehicleType.TRANSPORT_TRUCK,
            factions={HLLFaction.US},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=4,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=5,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=6,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=7,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=8,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=9,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=10,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=11,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def M3_HALF_TRACK(cls) -> "HLLVehicle":
        """*M3 Half-track*"""
        return cls(
            id="M3 Half-track",
            name="M3 Half-track",
            type=HLLVehicleType.HALF_TRACK,
            factions={HLLFaction.US},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_M2_BROWNING__M3_HALF_TRACK,
                    ],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=4,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=5,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=6,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=7,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def JEEP_WILLYS(cls) -> "HLLVehicle":
        """*Jeep Willys*"""
        return cls(
            id="Jeep Willys",
            name="Willy's Jeep",
            type=HLLVehicleType.JEEP,
            factions={HLLFaction.US},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def M4A3_105MM(cls) -> "HLLVehicle":
        """*M4A3 (105mm)*"""
        return cls(
            id="M4A3 (105mm)",
            name="Sherman M4(105)",
            type=HLLVehicleType.SELF_PROPELLED_ARTILLERY,
            factions={HLLFaction.US},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[
                        HLLWeapon.V_HULL_M1919__M4A3_105MM,
                    ],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_105MM_HOWITZER__M4A3_105MM,
                        HLLWeapon.V_COAXIAL_M1919__M4A3_105MM,
                    ],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def PAK_40(cls) -> "HLLVehicle":
        """*PAK 40*"""
        return cls(
            id="PAK 40",
            name="Pak 40",
            type=HLLVehicleType.ANTI_TANK_GUN,
            factions={HLLFaction.GER, HLLFaction.DAK},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[HLLWeapon.V_75MM_CANNON__PAK_40],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.LOADER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SFH_18(cls) -> "HLLVehicle":
        """*sFH 18*"""
        return cls(
            id="sFH 18",
            name="sFH 18",
            type=HLLVehicleType.ARTILLERY,
            factions={HLLFaction.GER, HLLFaction.DAK},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[HLLWeapon.V_150MM_HOWITZER__SFH_18],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.LOADER,
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SD_KFZ_234_PUMA(cls) -> "HLLVehicle":
        """*Sd.Kfz.234 Puma*"""
        return cls(
            id="Sd.Kfz.234 Puma",
            name="Sd.Kfz.234 Puma",
            type=HLLVehicleType.RECON_VEHICLE,
            factions={HLLFaction.GER, HLLFaction.DAK},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_50MM_KWK_91_1__SD_KFZ_234_PUMA,
                        HLLWeapon.V_COAXIAL_MG34__SD_KFZ_234_PUMA,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=4,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SD_KFZ_121_LUCHS(cls) -> "HLLVehicle":
        """*Sd.Kfz.121 Luchs*"""
        return cls(
            id="Sd.Kfz.121 Luchs",
            name="Sd.Kfz.121 Luchs",
            type=HLLVehicleType.LIGHT_TANK,
            factions={HLLFaction.GER, HLLFaction.DAK},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_20MM_KWK_30__SD_KFZ_121_LUCHS,
                        HLLWeapon.V_COAXIAL_MG34__SD_KFZ_121_LUCHS,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SD_KFZ_161_PANZER_IV(cls) -> "HLLVehicle":
        """*Sd.Kfz.161 Panzer IV*"""
        return cls(
            id="Sd.Kfz.161 Panzer IV",
            name="Sd.Kfz.161 Panzer IV",
            type=HLLVehicleType.MEDIUM_TANK,
            factions={HLLFaction.GER, HLLFaction.DAK},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[
                        HLLWeapon.V_HULL_MG34__SD_KFZ_161_PANZER_IV,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES | _HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_75MM_CANNON__SD_KFZ_161_PANZER_IV,
                        HLLWeapon.V_COAXIAL_MG34__SD_KFZ_161_PANZER_IV,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES | _HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES | _HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SD_KFZ_171_PANTHER(cls) -> "HLLVehicle":
        """*Sd.Kfz.171 Panther*"""
        return cls(
            id="Sd.Kfz.171 Panther",
            name="Sd.Kfz.171 Panther",
            type=HLLVehicleType.HEAVY_TANK,
            factions={HLLFaction.GER, HLLFaction.DAK},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[
                        HLLWeapon.V_HULL_MG34__SD_KFZ_171_PANTHER,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_75MM_CANNON__SD_KFZ_171_PANTHER,
                        HLLWeapon.V_COAXIAL_MG34__SD_KFZ_171_PANTHER,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SD_KFZ_181_TIGER_1(cls) -> "HLLVehicle":
        """*Sd.Kfz.181 Tiger 1*"""
        return cls(
            id="Sd.Kfz.181 Tiger 1",
            name="Sd.Kfz.181 Tiger 1",
            type=HLLVehicleType.HEAVY_TANK,
            factions={HLLFaction.GER, HLLFaction.DAK},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[
                        HLLWeapon.V_HULL_MG34__SD_KFZ_181_TIGER_1,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_88MM_KWK_36_L_56__SD_KFZ_181_TIGER_1,
                        HLLWeapon.V_COAXIAL_MG34__SD_KFZ_181_TIGER_1,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def OPEL_BLITZ_SUPPLY(cls) -> "HLLVehicle":
        """*Opel Blitz (Supply)*"""
        return cls(
            id="Opel Blitz (Supply)",
            name="Opel Blitz",
            type=HLLVehicleType.SUPPLY_TRUCK,
            factions={HLLFaction.GER, HLLFaction.DAK},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def OPEL_BLITZ_TRANSPORT(cls) -> "HLLVehicle":
        """*Opel Blitz (Transport)*"""
        return cls(
            id="Opel Blitz (Transport)",
            name="Opel Blitz",
            type=HLLVehicleType.TRANSPORT_TRUCK,
            factions={HLLFaction.GER, HLLFaction.DAK},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=4,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=5,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=6,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=7,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=8,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=9,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=10,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=11,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SD_KFZ_251_HALF_TRACK(cls) -> "HLLVehicle":
        """*Sd.Kfz 251 Half-track*"""
        return cls(
            id="Sd.Kfz 251 Half-track",
            name="Sd.Kfz 251 Half-track",
            type=HLLVehicleType.HALF_TRACK,
            factions={HLLFaction.GER, HLLFaction.DAK},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_M2_BROWNING__M3_HALF_TRACK,
                    ],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=4,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=5,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=6,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=7,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def KUBELWAGEN(cls) -> "HLLVehicle":
        """*Kubelwagen*"""
        return cls(
            id="Kubelwagen",
            name="Kubelwagen",
            type=HLLVehicleType.JEEP,
            factions={HLLFaction.GER, HLLFaction.DAK},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def STURMPANZER_IV(cls) -> "HLLVehicle":
        """*Sturmpanzer IV*"""
        return cls(
            id="Sturmpanzer IV",
            name="Sturmpanzer IV",
            type=HLLVehicleType.SELF_PROPELLED_ARTILLERY,
            factions={HLLFaction.GER},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_STUH_43_L_12__STURMPANZER_IV,
                    ],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def PANZER_III_AUSF_N(cls) -> "HLLVehicle":
        """*Panzer III Ausf.N*"""
        return cls(
            id="Panzer III Ausf.N",
            name="Panzer III",
            type=HLLVehicleType.SELF_PROPELLED_ARTILLERY,
            factions={HLLFaction.DAK},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[HLLWeapon.V_HULL_MG34__PANZER_III_AUSF_N],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_7_5CM_KWK_37__PANZER_III_AUSF_N,
                        HLLWeapon.V_COAXIAL_MG34__PANZER_III_AUSF_N,
                    ],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def ZIS_2(cls) -> "HLLVehicle":
        """*ZiS-2*"""
        return cls(
            id="ZiS-2",
            name="ZiS-2",
            type=HLLVehicleType.ANTI_TANK_GUN,
            factions={HLLFaction.SOV},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[HLLWeapon.V_57MM_CANNON__ZIS_2],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.LOADER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def M1938_M_30(cls) -> "HLLVehicle":
        """*M1938 (M-30)*"""
        return cls(
            id="M1938 (M-30)",
            name="M-30",
            type=HLLVehicleType.ARTILLERY,
            factions={HLLFaction.SOV},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[HLLWeapon.V_122MM_HOWITZER__M1938_M_30],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.LOADER,
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def BA_10(cls) -> "HLLVehicle":
        """*BA-10*"""
        return cls(
            id="BA-10",
            name="BA-10",
            type=HLLVehicleType.RECON_VEHICLE,
            factions={HLLFaction.SOV},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_19_K_45MM__BA_10,
                        HLLWeapon.V_COAXIAL_DT__BA_10,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=4,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def T70(cls) -> "HLLVehicle":
        """*T70*"""
        return cls(
            id="T70",
            name="T70",
            type=HLLVehicleType.LIGHT_TANK,
            factions={HLLFaction.SOV},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_45MM_M1937__T70,
                        HLLWeapon.V_COAXIAL_DT__T70,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def T34_76(cls) -> "HLLVehicle":
        """*T34/76*"""
        return cls(
            id="T34/76",
            name="T34/76",
            type=HLLVehicleType.MEDIUM_TANK,
            factions={HLLFaction.SOV},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[
                        HLLWeapon.V_HULL_DT__T34_76,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_76MM_ZIS_5__T34_76,
                        HLLWeapon.V_COAXIAL_DT__T34_76,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def IS_1(cls) -> "HLLVehicle":
        """*IS-1*"""
        return cls(
            id="IS-1",
            name="IS-1",
            type=HLLVehicleType.HEAVY_TANK,
            factions={HLLFaction.SOV},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[
                        HLLWeapon.V_HULL_DT__IS_1,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_D_5T_85MM__IS_1,
                        HLLWeapon.V_COAXIAL_DT__IS_1,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def ZIS_5_SUPPLY(cls) -> "HLLVehicle":
        """*ZIS-5 (Supply)*"""
        return cls(
            id="ZIS-5 (Supply)",
            name="ZIS-5",
            type=HLLVehicleType.SUPPLY_TRUCK,
            factions={HLLFaction.SOV},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def ZIS_5_TRANSPORT(cls) -> "HLLVehicle":
        """*ZIS-5 (Transport)*"""
        return cls(
            id="ZIS-5 (Transport)",
            name="ZIS-5",
            type=HLLVehicleType.TRANSPORT_TRUCK,
            factions={HLLFaction.SOV},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=4,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=5,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=6,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=7,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=8,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=9,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=10,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=11,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def GAZ_67(cls) -> "HLLVehicle":
        """*GAZ-67*"""
        return cls(
            id="GAZ-67",
            name="GAZ-67",
            type=HLLVehicleType.JEEP,
            factions={HLLFaction.SOV},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def KV_2(cls) -> "HLLVehicle":
        """*KV-2*"""
        return cls(
            id="KV-2",
            name="KV-2",
            type=HLLVehicleType.SELF_PROPELLED_ARTILLERY,
            factions={HLLFaction.SOV},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[HLLWeapon.V_HULL_DT__KV_2],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[HLLWeapon.V_152MM_M_10T__KV_2],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def QF_6_POUNDER(cls) -> "HLLVehicle":
        """*QF 6-Pounder*"""
        return cls(
            id="QF 6-Pounder",
            name="QF 6-Pounder",
            type=HLLVehicleType.ANTI_TANK_GUN,
            factions={HLLFaction.CW, HLLFaction.B8A},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[HLLWeapon.V_QF_6_POUNDER__QF_6_POUNDER],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.LOADER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def QF_25_POUNDER(cls) -> "HLLVehicle":
        """*QF 25-Pounder*"""
        return cls(
            id="QF 25-Pounder",
            name="QF 25-Pounder",
            type=HLLVehicleType.ARTILLERY,
            factions={HLLFaction.CW, HLLFaction.B8A},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[HLLWeapon.V_QF_25_POUNDER__QF_25_POUNDER],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.LOADER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def DAIMLER(cls) -> "HLLVehicle":
        """*Daimler*"""
        return cls(
            id="Daimler",
            name="Daimler",
            type=HLLVehicleType.RECON_VEHICLE,
            factions={HLLFaction.CW, HLLFaction.B8A},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_QF_2_POUNDER__DAIMLER,
                        HLLWeapon.V_COAXIAL_BESA__DAIMLER,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=4,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def TETRARCH(cls) -> "HLLVehicle":
        """*Tetrarch*"""
        return cls(
            id="Tetrarch",
            name="Tetrarch",
            type=HLLVehicleType.LIGHT_TANK,
            factions={HLLFaction.CW},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_QF_2_POUNDER__TETRARCH,
                        HLLWeapon.V_COAXIAL_BESA__TETRARCH,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def M3_STUART_HONEY(cls) -> "HLLVehicle":
        """*M3 Stuart Honey*"""
        return cls(
            id="M3 Stuart Honey",
            name="M3 Stuart Honey",
            type=HLLVehicleType.LIGHT_TANK,
            factions={HLLFaction.B8A},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[
                        HLLWeapon.V_HULL_M1919__M3_STUART_HONEY,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_37MM_CANNON__M3_STUART_HONEY,
                        HLLWeapon.V_COAXIAL_M1919__M3_STUART_HONEY,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CROMWELL(cls) -> "HLLVehicle":
        """*Cromwell*"""
        return cls(
            id="Cromwell",
            name="Cromwell",
            type=HLLVehicleType.MEDIUM_TANK,
            factions={HLLFaction.CW},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[
                        HLLWeapon.V_HULL_BESA__CROMWELL,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_OQF_75MM__CROMWELL,
                        HLLWeapon.V_COAXIAL_BESA__CROMWELL,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CRUSADER_MK_III(cls) -> "HLLVehicle":
        """*Crusader Mk.III*"""
        return cls(
            id="Crusader Mk.III",
            name="Crusader Mk III",
            type=HLLVehicleType.MEDIUM_TANK,
            factions={HLLFaction.B8A},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_OQF_57MM__CRUSADER_MK_III,
                        HLLWeapon.V_COAXIAL_BESA__CRUSADER_MK_III,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def FIREFLY(cls) -> "HLLVehicle":
        """*Firefly*"""
        return cls(
            id="Firefly",
            name="Sherman Firefly",
            type=HLLVehicleType.HEAVY_TANK,
            factions={HLLFaction.CW},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_QF_17_POUNDER__FIREFLY,
                        HLLWeapon.V_COAXIAL_M1919__FIREFLY,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CHURCHILL_MK_III(cls) -> "HLLVehicle":
        """*Churchill Mk.III*"""
        return cls(
            id="Churchill Mk.III",
            name="Churchill Mk III",
            type=HLLVehicleType.HEAVY_TANK,
            factions={HLLFaction.B8A},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[
                        HLLWeapon.V_HULL_BESA_7_92MM__CHURCHILL_MK_III,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_OQF_57MM__CHURCHILL_MK_III,
                        HLLWeapon.V_COAXIAL_BESA_7_92MM__CHURCHILL_MK_III,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CHURCHILL_MK_VII(cls) -> "HLLVehicle":
        """*Churchill Mk.VII*"""
        return cls(
            id="Churchill Mk.VII",
            name="Churchill Mk VII",
            type=HLLVehicleType.HEAVY_TANK,
            factions={HLLFaction.CW},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[
                        HLLWeapon.V_HULL_BESA_7_92MM__CHURCHILL_MK_VII,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_OQF_75MM__CHURCHILL_MK_VII,
                        HLLWeapon.V_COAXIAL_BESA_7_92MM__CHURCHILL_MK_VII,
                    ],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def BEDFORD_OYD_SUPPLY(cls) -> "HLLVehicle":
        """*Bedford OYD (Supply)*"""
        return cls(
            id="Bedford OYD (Supply)",
            name="Bedford OYD",
            type=HLLVehicleType.SUPPLY_TRUCK,
            factions={HLLFaction.CW, HLLFaction.B8A},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def BEDFORD_OYD_TRANSPORT(cls) -> "HLLVehicle":
        """*Bedford OYD (Transport)*"""
        return cls(
            id="Bedford OYD (Transport)",
            name="Bedford OYD",
            type=HLLVehicleType.TRANSPORT_TRUCK,
            factions={HLLFaction.CW, HLLFaction.B8A},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=4,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=5,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=6,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=7,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=8,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=9,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=10,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
                HLLVehicleSeat(
                    index=11,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    exposed=True,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CHURCHILL_MK_III_AVRE(cls) -> "HLLVehicle":
        """*Churchill Mk III A.V.R.E.*"""
        return cls(
            id="Churchill Mk III A.V.R.E.",
            name="Churchill AVRE",
            type=HLLVehicleType.SELF_PROPELLED_ARTILLERY,
            factions={HLLFaction.CW},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[HLLWeapon.V_HULL_BESA_7_92MM__CHURCHILL_MK_III_AVRE],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[
                        HLLWeapon.V_230MM_PETARD__CHURCHILL_MK_III_AVRE,
                        HLLWeapon.V_COAXIAL_BESA_7_92MM__CHURCHILL_MK_III_AVRE,
                    ],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def BISHOP_SP_25PDR(cls) -> "HLLVehicle":
        """*Bishop SP 25pdr*"""
        return cls(
            id="Bishop SP 25pdr",
            name="Bishop",
            type=HLLVehicleType.SELF_PROPELLED_ARTILLERY,
            factions={HLLFaction.B8A},
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[HLLWeapon.V_QF_25_POUNDER__BISHOP_SP_25PDR],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.SPOTTER,
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )


class HLLVVehicle(_Vehicle[HLLVFaction, HLLVVehicleSeat, HLLVVehicleType]):
    pass


Vehicle: TypeAlias = HLLVehicle | HLLVVehicle
