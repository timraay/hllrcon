# ruff: noqa: N802, D400, D415, RUF100

from enum import StrEnum
from typing import Annotated, Generic, TypeAlias, TypeVar

from pydantic import BaseModel, Field

from hllrcon.data._utils import (
    IndexedBaseModel,
    class_cached_property,  # noqa: F401
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
    COMMANDER = "Commander"
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
    ### INJECT "hll vehicles" START

    @class_cached_property
    @classmethod
    def BA_10(cls) -> "HLLVehicle":
        """*BA-10*"""
        return cls(
            id="BA-10",
            name="BA-10",
            factions={HLLFaction.SOV},
            type=HLLVehicleType.RECON_VEHICLE,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
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
            name="Bedford OYD (Supply)",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLVehicleType.SUPPLY_TRUCK,
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def BEDFORD_OYD_TRANSPORT(cls) -> "HLLVehicle":
        """*Bedford OYD (Transport)*"""
        return cls(
            id="Bedford OYD (Transport)",
            name="Bedford OYD (Transport)",
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLVehicleType.TRANSPORT_TRUCK,
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=4,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=5,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=6,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=7,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=8,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=9,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=10,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=11,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
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
            name="Bishop SP 25pdr",
            factions={HLLFaction.B8A},
            type=HLLVehicleType.SELF_PROPELLED_ARTILLERY,
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
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CHURCHILL_MK_III_AVRE(cls) -> "HLLVehicle":
        """*Churchill Mk III A.V.R.E.*"""
        return cls(
            id="Churchill Mk III A.V.R.E.",
            name="Churchill Mk III A.V.R.E.",
            factions={HLLFaction.CW},
            type=HLLVehicleType.SELF_PROPELLED_ARTILLERY,
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
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CHURCHILL_MKIII(cls) -> "HLLVehicle":
        """*Churchill Mk.III*"""
        return cls(
            id="Churchill Mk.III",
            name="Churchill Mk.III",
            factions={HLLFaction.B8A},
            type=HLLVehicleType.HEAVY_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CHURCHILL_MKVII(cls) -> "HLLVehicle":
        """*Churchill Mk.VII*"""
        return cls(
            id="Churchill Mk.VII",
            name="Churchill Mk.VII",
            factions={HLLFaction.CW},
            type=HLLVehicleType.HEAVY_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
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
            factions={HLLFaction.CW},
            type=HLLVehicleType.MEDIUM_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CRUSADER_MKIII(cls) -> "HLLVehicle":
        """*Crusader Mk.III*"""
        return cls(
            id="Crusader Mk.III",
            name="Crusader Mk.III",
            factions={HLLFaction.B8A},
            type=HLLVehicleType.MEDIUM_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
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
            factions={HLLFaction.CW, HLLFaction.B8A},
            type=HLLVehicleType.RECON_VEHICLE,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
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
            name="Firefly",
            factions={HLLFaction.CW},
            type=HLLVehicleType.HEAVY_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
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
            factions={HLLFaction.SOV},
            type=HLLVehicleType.JEEP,
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
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
            name="GMC CCKW 353 (Supply)",
            factions={HLLFaction.US},
            type=HLLVehicleType.SUPPLY_TRUCK,
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def GMC_CCKW_353_TRANSPORT(cls) -> "HLLVehicle":
        """*GMC CCKW 353 (Transport)*"""
        return cls(
            id="GMC CCKW 353 (Transport)",
            name="GMC CCKW 353 (Transport)",
            factions={HLLFaction.US},
            type=HLLVehicleType.TRANSPORT_TRUCK,
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=4,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=5,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=6,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=7,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=8,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=9,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=10,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=11,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
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
            factions={HLLFaction.SOV},
            type=HLLVehicleType.HEAVY_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def JEEP_WILLYS(cls) -> "HLLVehicle":
        """*Jeep Willys*"""
        return cls(
            id="Jeep Willys",
            name="Jeep Willys",
            factions={HLLFaction.US, HLLFaction.CW, HLLFaction.B8A},
            type=HLLVehicleType.JEEP,
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
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
            factions={HLLFaction.SOV},
            type=HLLVehicleType.SELF_PROPELLED_ARTILLERY,
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
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
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
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLVehicleType.JEEP,
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
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
            factions={HLLFaction.US, HLLFaction.SOV, HLLFaction.CW, HLLFaction.B8A},
            type=HLLVehicleType.HALF_TRACK,
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=4,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=5,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=6,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=7,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
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
            factions={HLLFaction.B8A},
            type=HLLVehicleType.LIGHT_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def M4A3_105MM(cls) -> "HLLVehicle":
        """*M4A3 (105mm)*"""
        return cls(
            id="M4A3 (105mm)",
            name="M4A3 (105mm)",
            factions={HLLFaction.US},
            type=HLLVehicleType.SELF_PROPELLED_ARTILLERY,
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
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
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
            factions={HLLFaction.US},
            type=HLLVehicleType.RECON_VEHICLE,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
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
            name="Opel Blitz (Supply)",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLVehicleType.SUPPLY_TRUCK,
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def OPEL_BLITZ_TRANSPORT(cls) -> "HLLVehicle":
        """*Opel Blitz (Transport)*"""
        return cls(
            id="Opel Blitz (Transport)",
            name="Opel Blitz (Transport)",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLVehicleType.TRANSPORT_TRUCK,
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=4,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=5,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=6,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=7,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=8,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=9,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=10,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=11,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def PANZER_III_AUSFN(cls) -> "HLLVehicle":
        """*Panzer III Ausf.N*"""
        return cls(
            id="Panzer III Ausf.N",
            name="Panzer III Ausf.N",
            factions={HLLFaction.DAK},
            type=HLLVehicleType.SELF_PROPELLED_ARTILLERY,
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
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SDKFZ_251_HALF_TRACK(cls) -> "HLLVehicle":
        """*Sd.Kfz 251 Half-track*"""
        return cls(
            id="Sd.Kfz 251 Half-track",
            name="Sd.Kfz 251 Half-track",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLVehicleType.HALF_TRACK,
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.GUNNER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=4,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=5,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=6,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=7,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SDKFZ121_LUCHS(cls) -> "HLLVehicle":
        """*Sd.Kfz.121 Luchs*"""
        return cls(
            id="Sd.Kfz.121 Luchs",
            name="Sd.Kfz.121 Luchs",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLVehicleType.LIGHT_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SDKFZ161_PANZER_IV(cls) -> "HLLVehicle":
        """*Sd.Kfz.161 Panzer IV*"""
        return cls(
            id="Sd.Kfz.161 Panzer IV",
            name="Sd.Kfz.161 Panzer IV",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLVehicleType.MEDIUM_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SDKFZ171_PANTHER(cls) -> "HLLVehicle":
        """*Sd.Kfz.171 Panther*"""
        return cls(
            id="Sd.Kfz.171 Panther",
            name="Sd.Kfz.171 Panther",
            factions={HLLFaction.GER},
            type=HLLVehicleType.HEAVY_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SDKFZ181_TIGER_1(cls) -> "HLLVehicle":
        """*Sd.Kfz.181 Tiger 1*"""
        return cls(
            id="Sd.Kfz.181 Tiger 1",
            name="Sd.Kfz.181 Tiger 1",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLVehicleType.HEAVY_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SDKFZ234_PUMA(cls) -> "HLLVehicle":
        """*Sd.Kfz.234 Puma*"""
        return cls(
            id="Sd.Kfz.234 Puma",
            name="Sd.Kfz.234 Puma",
            factions={HLLFaction.GER, HLLFaction.DAK},
            type=HLLVehicleType.RECON_VEHICLE,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SHERMAN_M4A375W(cls) -> "HLLVehicle":
        """*Sherman M4A3(75)W*"""
        return cls(
            id="Sherman M4A3(75)W",
            name="Sherman M4A3(75)W",
            factions={HLLFaction.US},
            type=HLLVehicleType.MEDIUM_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
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
            name="Sherman M4A3E2",
            factions={HLLFaction.US},
            type=HLLVehicleType.HEAVY_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def SHERMAN_M4A3E276(cls) -> "HLLVehicle":
        """*Sherman M4A3E2(76)*"""
        return cls(
            id="Sherman M4A3E2(76)",
            name="Sherman M4A3E2(76)",
            factions={HLLFaction.US},
            type=HLLVehicleType.HEAVY_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
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
            name="Stuart M5A1",
            factions={HLLFaction.US},
            type=HLLVehicleType.LIGHT_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
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
            factions={HLLFaction.GER},
            type=HLLVehicleType.SELF_PROPELLED_ARTILLERY,
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
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_ARTY_CREW_ROLES,
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
            factions={HLLFaction.SOV},
            type=HLLVehicleType.MEDIUM_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
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
            factions={HLLFaction.SOV},
            type=HLLVehicleType.LIGHT_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
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
            factions={HLLFaction.CW},
            type=HLLVehicleType.LIGHT_TANK,
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
                    weapons=[],
                    requires_roles=_HLL_TANK_CREW_ROLES,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.COMMANDER,
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
            name="ZIS-5 (Supply)",
            factions={HLLFaction.SOV},
            type=HLLVehicleType.SUPPLY_TRUCK,
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def ZIS_5_TRANSPORT(cls) -> "HLLVehicle":
        """*ZIS-5 (Transport)*"""
        return cls(
            id="ZIS-5 (Transport)",
            name="ZIS-5 (Transport)",
            factions={HLLFaction.SOV},
            type=HLLVehicleType.TRANSPORT_TRUCK,
            seats=[
                HLLVehicleSeat(
                    index=0,
                    type=HLLVehicleSeatType.DRIVER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=1,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=2,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=3,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=4,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=5,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=6,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=7,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=8,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=9,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=10,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
                HLLVehicleSeat(
                    index=11,
                    type=HLLVehicleSeatType.PASSENGER,
                    weapons=[],
                    requires_roles=None,
                    exposed=False,
                ),
            ],
        )

    ### INJECT "hll vehicles" END


class HLLVVehicle(_Vehicle[HLLVFaction, HLLVVehicleSeat, HLLVVehicleType]):
    pass


Vehicle: TypeAlias = HLLVehicle | HLLVVehicle
