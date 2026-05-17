from collections.abc import Iterator
from enum import StrEnum
from typing import Annotated, Any, Generic

from pydantic import Field
from typing_extensions import TypeVar

from scripts.extractlib.loader import Model, Object, ObjectReference
from scripts.extractlib.objects.blueprint_generated_class import (
    BGCReference,
)
from scripts.extractlib.objects.hll_armor_health_component import (
    HLLArmorHealthComponent,
)
from scripts.extractlib.objects.hll_armor_inventory import HLLArmorInventory
from scripts.extractlib.objects.tank_seat import (
    ArtillerySeat,
    SelfPropelledArtillerySeat,
    TankSeat,
    VehicleSeat,
)
from scripts.extractlib.structs.team import ETeam
from scripts.extractlib.types import String


class EHLLArmorWeightClass(StrEnum):
    LIGHT = "EHLLArmourWeightClass::AR_Light"
    MEDIUM = "EHLLArmourWeightClass::AR_Medium"
    HEAVY = "EHLLArmourWeightClass::AR_Heavy"


class WFLBaseTankPropertiesMetaData(Model):
    score_type: str | None = None
    display_name: String


class HLLVehicleProperties(Model):
    armor_collision_body: Annotated[
        ObjectReference[Any] | None,
        Field(alias="ArmourCollision_Body"),
    ] = None
    armor_collision_tracks: Annotated[
        ObjectReference[Any] | None,
        Field(alias="ArmourCollision_Tracks"),
    ] = None
    armor_collision_turret: Annotated[
        ObjectReference[Any] | None,
        Field(alias="ArmourCollision_Turret"),
    ] = None
    armor_collision_barrel: Annotated[
        ObjectReference[Any] | None,
        Field(alias="ArmourCollision_Barrel"),
    ] = None
    engine_warmup_duration: float = 0.0
    armor_health: Annotated[
        ObjectReference[HLLArmorHealthComponent],
        Field(alias="ArmourHealth"),
    ]
    armor_inventory: Annotated[
        ObjectReference[HLLArmorInventory],
        Field(alias="ArmourInventory"),
    ]
    armor_meta_data: Annotated[
        WFLBaseTankPropertiesMetaData,
        Field(alias="ArmourMetaData"),
    ]
    armor_weight_class: Annotated[
        EHLLArmorWeightClass | None,
        Field(alias="ArmourWeightClass"),
    ] = None
    low_speed_threshold_kph: float = 0.0
    team: ETeam

    def get_seats(self) -> Iterator[VehicleSeat]:
        yield from []


class HLLArmorProperties(HLLVehicleProperties):
    driver_seat_class: BGCReference[TankSeat]
    gunner_seat_class: BGCReference[TankSeat]
    commander_seat_class: BGCReference[TankSeat]
    turret_controller2: ObjectReference[Any]

    def get_driver_seat(self) -> TankSeat:
        return self.driver_seat_class.get_inst(TankSeat)

    def get_gunner_seat(self) -> TankSeat:
        return self.gunner_seat_class.get_inst(TankSeat)

    def get_commander_seat(self) -> TankSeat:
        return self.commander_seat_class.get_inst(TankSeat)

    def get_seats(self) -> Iterator[VehicleSeat]:
        yield from super().get_seats()
        yield self.get_driver_seat()
        yield self.get_gunner_seat()
        yield self.get_commander_seat()


class HLLReconVehicleProperties(HLLArmorProperties):
    first_passenger_seat_class: BGCReference[VehicleSeat]
    second_passenger_seat_class: BGCReference[VehicleSeat]

    def get_first_passenger_seat(self) -> VehicleSeat:
        return self.first_passenger_seat_class.get_inst(VehicleSeat)

    def get_second_passenger_seat(self) -> VehicleSeat:
        return self.second_passenger_seat_class.get_inst(VehicleSeat)

    def get_seats(self) -> Iterator[VehicleSeat]:
        yield from super().get_seats()
        yield self.get_first_passenger_seat()
        yield self.get_second_passenger_seat()


class HLLSelfPropelledArtilleryProperties(HLLArmorProperties):
    driver_seat_class: BGCReference[SelfPropelledArtillerySeat]
    gunner_seat_class: BGCReference[SelfPropelledArtillerySeat]
    commander_seat_class: BGCReference[SelfPropelledArtillerySeat]

    def get_driver_seat(self) -> SelfPropelledArtillerySeat:
        return self.driver_seat_class.get_inst(SelfPropelledArtillerySeat)

    def get_gunner_seat(self) -> SelfPropelledArtillerySeat:
        return self.gunner_seat_class.get_inst(SelfPropelledArtillerySeat)

    def get_commander_seat(self) -> SelfPropelledArtillerySeat:
        return self.commander_seat_class.get_inst(SelfPropelledArtillerySeat)


class HLLTruckProperties(HLLVehicleProperties):
    num_back_passenger_seats: int = 10
    driver_seat_class: BGCReference[VehicleSeat]
    front_passenger_seat_class: BGCReference[VehicleSeat]
    back_passenger_seat_class: BGCReference[VehicleSeat]

    def get_driver_seat(self) -> VehicleSeat:
        return self.driver_seat_class.get_inst(VehicleSeat)

    def get_front_passenger_seat(self) -> VehicleSeat:
        return self.front_passenger_seat_class.get_inst(VehicleSeat)

    def get_back_passenger_seat(self) -> VehicleSeat:
        return self.back_passenger_seat_class.get_inst(VehicleSeat)

    def get_seats(self) -> Iterator[VehicleSeat]:
        yield from super().get_seats()
        yield self.get_driver_seat()
        yield self.get_front_passenger_seat()
        for _ in range(self.num_back_passenger_seats):
            yield self.get_back_passenger_seat()


class HLLHalftrackProperties(HLLTruckProperties):
    turret_controller: ObjectReference[Any] | None = None


class HLLAntiTankGunProperties(HLLVehicleProperties):
    gunner_seat_class: BGCReference[VehicleSeat]
    loader_seat_class: BGCReference[VehicleSeat]

    def get_gunner_seat(self) -> VehicleSeat:
        return self.gunner_seat_class.get_inst(VehicleSeat)

    def get_loader_seat(self) -> VehicleSeat:
        return self.loader_seat_class.get_inst(VehicleSeat)

    def get_seats(self) -> Iterator[VehicleSeat]:
        yield from super().get_seats()
        yield self.get_gunner_seat()
        yield self.get_loader_seat()


class HLLHowitzerProperties(HLLAntiTankGunProperties):
    gunner_seat_class: BGCReference[ArtillerySeat]
    loader_seat_class: BGCReference[ArtillerySeat]

    def get_gunner_seat(self) -> ArtillerySeat:
        return self.gunner_seat_class.get_inst(ArtillerySeat)

    def get_loader_seat(self) -> ArtillerySeat:
        return self.loader_seat_class.get_inst(ArtillerySeat)


HLLVehiclePropT_co = TypeVar(
    "HLLVehiclePropT_co",
    bound=HLLVehicleProperties,
    default=HLLArmorProperties
    | HLLReconVehicleProperties
    | HLLSelfPropelledArtilleryProperties
    | HLLHalftrackProperties
    | HLLTruckProperties
    | HLLHowitzerProperties
    | HLLAntiTankGunProperties,
    covariant=True,
)


class HLLVehicle(Object[HLLVehiclePropT_co], Generic[HLLVehiclePropT_co]):
    pass
