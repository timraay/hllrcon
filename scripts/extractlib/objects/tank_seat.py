from typing import Annotated, Generic, TypeVar

from pydantic import Field

from scripts.extractlib.loader import Model, Object
from scripts.extractlib.types import String


class VehicleSeatProperties(Model):
    seat_display_name: String
    entry_time: float = 1.0
    switch_time: float = 2.0
    exit_time: float = 1.0
    only_allow_armor_units_in: Annotated[
        bool,
        Field(alias="bOnlyAllowArmourUnitsIn"),
    ] = False
    block_tank_roles: Annotated[
        bool,
        Field(alias="bBlockTankRoles"),
    ] = False
    block_artillery_roles: Annotated[
        bool,
        Field(alias="bBlockArtilleryRoles"),
    ] = False


class TankSeatProperties(VehicleSeatProperties):
    only_allow_armor_units_in: Annotated[
        bool,
        Field(alias="bOnlyAllowArmourUnitsIn"),
    ] = True
    block_tank_roles: Annotated[
        bool,
        Field(alias="bBlockTankRoles"),
    ] = False
    block_artillery_roles: Annotated[
        bool,
        Field(alias="bBlockArtilleryRoles"),
    ] = True


class SelfPropelledArtillerySeatProperties(TankSeatProperties):
    only_allow_armor_units_in: Annotated[
        bool,
        Field(alias="bOnlyAllowArmourUnitsIn"),
    ] = True
    block_tank_roles: Annotated[
        bool,
        Field(alias="bBlockTankRoles"),
    ] = True
    block_artillery_roles: Annotated[
        bool,
        Field(alias="bBlockArtilleryRoles"),
    ] = False


VehicleSeatPropertiesT_co = TypeVar(
    "VehicleSeatPropertiesT_co",
    bound=VehicleSeatProperties,
    default=VehicleSeatProperties,
    covariant=True,
)

TankSeatPropertiesT_co = TypeVar(
    "TankSeatPropertiesT_co",
    bound=TankSeatProperties,
    default=TankSeatProperties,
    covariant=True,
)


class VehicleSeat(
    Object[VehicleSeatPropertiesT_co],
    Generic[VehicleSeatPropertiesT_co],
):
    pass


class TankSeat(VehicleSeat[TankSeatPropertiesT_co], Generic[TankSeatPropertiesT_co]):
    pass


class SelfPropelledArtillerySeat(
    TankSeat[SelfPropelledArtillerySeatProperties],
):
    pass
