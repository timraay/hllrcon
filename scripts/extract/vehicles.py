import itertools
import logging
from abc import ABC, abstractmethod
from collections.abc import Iterator
from enum import StrEnum
from pathlib import Path
from typing import Generic, cast

from pydantic import BaseModel, TypeAdapter, model_validator

from hllrcon.data.factions import HLLFaction
from hllrcon.data.vehicles import HLLVehicleType, VehicleType
from hllrcon.data.weapons import HLLWeaponType
from scripts.extract.utils import (
    inject_code,
    stringify_factions,
    stringify_list,
    to_method_name,
)
from scripts.extract.weapons import WeaponData
from scripts.extractlib.loader import (
    load_object_from_file,
    local_to_abs_path,
)
from scripts.extractlib.objects.blueprint_generated_class import BlueprintGeneratedClass
from scripts.extractlib.objects.hll_armor_health_component import (
    HLLArmorHealthComponent,
)
from scripts.extractlib.objects.hll_armor_inventory import HLLArmorInventory
from scripts.extractlib.objects.hll_armor_weapon import (
    EShellType,
    HLLArmorWeapon,
    HLLArmorWeaponBallistic,
    HLLArmorWeaponMountedHowitzer,
    HLLArmorWeaponProjectile,
    HLLArmorWeaponReconGun,
    HLLArmorWeaponSmokeScreen,
)
from scripts.extractlib.objects.hll_commander_ability import (
    HLLCommanderAbility,
    HLLCommanderAbilitySpawnVehicleProperties,
)
from scripts.extractlib.objects.hll_map_ability_data import HLLMapAbilityData
from scripts.extractlib.objects.hll_vehicle import (
    HLLArmorProperties,
    HLLHalftrackProperties,
    HLLSelfPropelledArtilleryProperties,
    HLLTruckProperties,
    HLLVehicle,
    HLLVehiclePropT_co,
)
from scripts.extractlib.objects.tank_seat import VehicleSeat

logger = logging.getLogger(__name__)

HLL_VEHICLE_CONSTRUCTOR_TEMPLATE = """\
    @class_cached_property
    @classmethod
    def {vehicle.meth_name}(cls) -> "HLLVehicle":
        \"\"\"*{vehicle.id}*\"\"\"
        return cls(
            id="{vehicle.id}",
            name="{vehicle.name}",
            factions={factions},
            type=HLLVehicleType.{vehicle.type.name},
            seats={seats},
        )"""

# TODO: weapons, requires_roles, exposed
HLL_VEHICLE_SEAT_CONSTRUCTOR_TEMPLATE = """\
HLLVehicleSeat(
    index={index},
    type=HLLVehicleSeatType.{seat.name},
    weapons={weapons},
    requires_roles={requires_roles},
    exposed=False,
)"""


class VehicleWeaponAmmoType(StrEnum):
    AP = "AP"
    HE = "HE"
    MG = "MG"
    RECON = "Recon"
    SMOKE = "Smoke"

    @classmethod
    def from_shell_type(
        cls,
        shell_type: EShellType,
    ) -> "VehicleWeaponAmmoType | None":
        if shell_type == EShellType.AP:
            return cls.AP
        if shell_type == EShellType.HE:
            return cls.HE
        if shell_type == EShellType.MAX:
            return cls.SMOKE
        return None


class VehicleSeatRoleTypes(StrEnum):
    ALL = "all"
    TANK_CREW = "tank_crew"
    ARTY_CREW = "arty_crew"


class VehicleCompartmentData(BaseModel):
    health: float


class VehicleWeaponAmmo(BaseModel):
    munitions_cost: int
    clip_size: int
    max_clips: int
    name: str
    type: VehicleWeaponAmmoType
    explosion_damage: float
    explosion_radius: float
    # TODO: Penetration?
    # TODO: Suppression radius?


class VehicleWeapon(BaseModel):
    name: str
    type: HLLWeaponType
    ammo: list[VehicleWeaponAmmo]


class VehicleSeatData(BaseModel):
    name: str
    weapons: list[VehicleWeapon]
    role_types: VehicleSeatRoleTypes
    entry_time: float
    switch_time: float
    exit_time: float

    def get_weapons(
        self,
        vehicle_data: "VehicleData",
        *,
        include_generic: bool = False,
    ) -> list[WeaponData]:
        weapons: list[WeaponData] = []
        for weapon in self.weapons:
            weapon_id = f"{weapon.name} [{vehicle_data.id}]"
            meth_name = "V_" + to_method_name(weapon_id)
            weapons.append(
                WeaponData(
                    meth_name=meth_name,
                    id=weapon_id,
                    name=weapon.name,
                    vehicle_id=vehicle_data.id,
                    factions=vehicle_data.factions,
                    type=weapon.type,
                ),
            )
            if include_generic:
                generic_weapon_id = weapon.name
                generic_meth_name = (
                    "V_" + to_method_name(generic_weapon_id) + "__UNKNOWN"
                )
                weapons.append(
                    WeaponData(
                        meth_name=generic_meth_name,
                        id=generic_weapon_id,
                        name=weapon.name,
                        vehicle_id=None,
                        factions=vehicle_data.factions,
                        type=weapon.type,
                    ),
                )
        return weapons

    @staticmethod
    def merge(
        seat1: "VehicleSeatData",
        seat2: "VehicleSeatData",
    ) -> "VehicleSeatData":
        for prop_name in (
            "name",
            "weapons",
            "role_types",
            "entry_time",
            "switch_time",
            "exit_time",
        ):
            prop1 = getattr(seat1, prop_name)
            prop2 = getattr(seat2, prop_name)
            if prop1 != prop2:
                logger.warning(
                    "Inconsistent property VehicleSeatData.%s when merging: %s != %s",
                    prop_name,
                    prop1,
                    prop2,
                )

        return VehicleSeatData(
            name=seat1.name,
            weapons=seat1.weapons,
            role_types=seat1.role_types,
            entry_time=max(seat1.entry_time, seat2.entry_time),
            switch_time=max(seat1.switch_time, seat2.switch_time),
            exit_time=max(seat1.exit_time, seat2.exit_time),
        )


class VehicleData(BaseModel):
    meth_name: str = ""
    blueprint_ids: set[str]
    id: str
    name: str
    type: VehicleType
    factions: set[HLLFaction]
    hull: VehicleCompartmentData
    turret: VehicleCompartmentData
    tracks: VehicleCompartmentData
    engine: VehicleCompartmentData
    seats: list[VehicleSeatData] = []

    @model_validator(mode="after")
    def set_meth_name(self) -> "VehicleData":
        if not self.meth_name:
            self.meth_name = to_method_name(self.id)
        return self

    def get_weapons(self, *, include_generic: bool = False) -> list[WeaponData]:
        weapons: list[WeaponData] = []
        weapons.append(
            WeaponData(
                meth_name="V_ROADKILL__" + to_method_name(self.id),
                id=self.id,
                name=self.id,
                vehicle_id=self.id,
                factions=self.factions,
                type=HLLWeaponType.ROADKILL,
            ),
        )
        for seat in self.seats:
            weapons.extend(seat.get_weapons(self, include_generic=include_generic))
        return weapons

    def to_constructor(self) -> str:
        seats: list[str] = []
        for index, seat in enumerate(self.seats):
            if seat.role_types == VehicleSeatRoleTypes.TANK_CREW:
                requires_roles = "_HLL_TANK_CREW_ROLES"
            elif seat.role_types == VehicleSeatRoleTypes.ARTY_CREW:
                requires_roles = "_HLL_ARTY_CREW_ROLES"
            else:
                requires_roles = "None"

            weapons = stringify_list(
                [f"HLLWeapon.{weapon.meth_name}" for weapon in seat.get_weapons(self)],
                indent=4,
            ).lstrip()

            seats.append(
                HLL_VEHICLE_SEAT_CONSTRUCTOR_TEMPLATE.format(
                    index=index,
                    seat=seat,
                    weapons=weapons,
                    requires_roles=requires_roles,
                ),
            )

        return HLL_VEHICLE_CONSTRUCTOR_TEMPLATE.format(
            vehicle=self,
            factions=stringify_factions(self.factions),
            seats=stringify_list(seats, indent=3 * 4).lstrip(),
        )

    @staticmethod
    def merge(*vd_seq: "VehicleData") -> "VehicleData":
        if not vd_seq:
            msg = "At least one VehicleData must be provided"
            raise ValueError(msg)

        if len(vd_seq) == 1:
            return vd_seq[0]

        vd1 = vd_seq[0]
        vd2 = vd_seq[1]

        for prop_name in ("id", "name", "type", "hull", "turret", "tracks", "engine"):
            prop1 = getattr(vd1, prop_name)
            prop2 = getattr(vd2, prop_name)
            if prop1 != prop2:
                logger.warning(
                    "Inconsistent property VehicleData.%s when merging (%s, %s):"
                    " %s != %s",
                    prop_name,
                    vd1.blueprint_ids,
                    vd2.blueprint_ids,
                    prop1,
                    prop2,
                )
        if len(vd1.seats) != len(vd2.seats):
            msg = "VehicleData seats number must match"
            raise ValueError(msg)

        vd_merged = VehicleData(
            blueprint_ids=vd1.blueprint_ids | vd2.blueprint_ids,
            id=vd1.id,
            name=vd1.name,
            type=vd1.type,
            factions=vd1.factions.union(vd2.factions),
            hull=vd1.hull,
            turret=vd1.turret,
            tracks=vd1.tracks,
            engine=vd1.engine,
            seats=[
                VehicleSeatData.merge(seat1, seat2)
                for seat1, seat2 in zip(vd1.seats, vd2.seats, strict=True)
            ],
        )

        return VehicleData.merge(vd_merged, *vd_seq[2:])


class VehicleExtractor(ABC, Generic[HLLVehiclePropT_co]):
    def __init__(
        self,
        vehicle: HLLVehicle[HLLVehiclePropT_co],
        vehicle_type: VehicleType,
        factions: set[HLLFaction],
    ) -> None:
        self.vehicle = vehicle
        self.vehicle_type = vehicle_type
        self.factions = factions

    def seat_component_to_model(self, component: VehicleSeat) -> VehicleSeatData:
        role_types = VehicleSeatRoleTypes.ALL
        if component.properties.only_allow_armor_units_in:
            if (
                component.properties.block_tank_roles
                == component.properties.block_artillery_roles
            ):
                logger.error(
                    "Unexpected seat properties with bOnlyAllowArmourUnitsIn=True and"
                    " bBlockTankRoles==bBlockArtilleryRoles",
                )

            elif component.properties.block_tank_roles:
                role_types = VehicleSeatRoleTypes.ARTY_CREW
            elif component.properties.block_artillery_roles:
                role_types = VehicleSeatRoleTypes.TANK_CREW

        return VehicleSeatData(
            name=str(component.properties.seat_display_name),
            weapons=[],
            role_types=role_types,
            entry_time=component.properties.entry_time,
            switch_time=component.properties.switch_time,
            exit_time=component.properties.exit_time,
        )

    def get_weapon_type(self, weapon: HLLArmorWeapon, seat_index: int) -> HLLWeaponType:  # noqa: ARG002
        msg = "Cannot determine weapon type"
        raise ValueError(msg)

    @abstractmethod
    def extract(self) -> VehicleData: ...


class ArmoredVehicleExtractor(
    VehicleExtractor[HLLArmorProperties | HLLSelfPropelledArtilleryProperties],
):
    def get_weapon_type(self, weapon: HLLArmorWeapon, seat_index: int) -> HLLWeaponType:
        if seat_index == 0:
            return HLLWeaponType.TANK_HULL_MG
        if seat_index == 1:
            if isinstance(weapon, HLLArmorWeaponBallistic):
                return HLLWeaponType.TANK_COAXIAL_MG
            return HLLWeaponType.TANK_CANNON
        if seat_index == 2:
            # Recon gun
            return HLLWeaponType.NON_LETHAL

        return super().get_weapon_type(weapon, seat_index)

    def extract(self) -> VehicleData:  # noqa: C901, PLR0912
        meta_data = self.vehicle.properties.armor_meta_data
        health = self.vehicle.properties.armor_health.get(HLLArmorHealthComponent)
        inventory = self.vehicle.properties.armor_inventory.get(HLLArmorInventory)

        driver_seat = self.vehicle.properties.get_driver_seat()
        gunner_seat = self.vehicle.properties.get_gunner_seat()
        commander_seat = self.vehicle.properties.get_commander_seat()
        # TODO: RV passenger seats

        seats = [
            self.seat_component_to_model(driver_seat),
            self.seat_component_to_model(gunner_seat),
            self.seat_component_to_model(commander_seat),
        ]

        for inventory_item in inventory.properties.default_inventory:
            seat_index = inventory_item.owning_seat_index
            weapon = inventory_item.get_weapon()
            weapon_type = self.get_weapon_type(weapon, seat_index)

            weapon_data = VehicleWeapon(
                name=str(weapon.properties.weapon_name),
                type=weapon_type,
                ammo=[],
            )
            seats[seat_index].weapons.append(weapon_data)

            ammo_sources = weapon.properties.ammo_info.ammo_sources
            if isinstance(weapon, HLLArmorWeaponBallistic):
                for ammo_source in ammo_sources:
                    weapon_data.ammo.append(
                        VehicleWeaponAmmo(
                            munitions_cost=0,
                            clip_size=ammo_source.clip_size,
                            max_clips=ammo_source.max_clips,
                            name=str(ammo_source.display_name),
                            type=VehicleWeaponAmmoType.MG,
                            explosion_damage=0,
                            explosion_radius=0,
                        ),
                    )
            elif isinstance(
                weapon,
                HLLArmorWeaponProjectile,
            ):
                projectiles = weapon.get_projectiles()
                for ammo_source, projectile in zip(
                    ammo_sources,
                    projectiles,
                    strict=True,
                ):
                    ammo_type = VehicleWeaponAmmoType.from_shell_type(
                        ammo_source.shell_type,
                    )
                    if not ammo_type:
                        logger.error(
                            "Cannot determine ammo type for source %s",
                            ammo_source,
                        )
                        ammo_type = VehicleWeaponAmmoType.AP
                    weapon_data.ammo.append(
                        VehicleWeaponAmmo(
                            munitions_cost=0,
                            clip_size=ammo_source.clip_size,
                            max_clips=ammo_source.max_clips,
                            name=str(ammo_source.display_name),
                            type=ammo_type,
                            explosion_damage=projectile.properties.explosion_damage,
                            explosion_radius=projectile.properties.explosion_radius,
                        ),
                    )
            elif isinstance(
                weapon,
                HLLArmorWeaponMountedHowitzer,
            ):
                projectiles = weapon.get_projectiles()
                for ammo_source, projectile in zip(
                    ammo_sources,
                    projectiles,
                    strict=True,
                ):
                    if projectile.properties.explosion_damage == 0:
                        ammo_type = VehicleWeaponAmmoType.SMOKE
                    elif projectile.properties.explosion_radius > 3000:
                        ammo_type = VehicleWeaponAmmoType.HE
                    else:
                        ammo_type = VehicleWeaponAmmoType.AP

                    weapon_data.ammo.append(
                        VehicleWeaponAmmo(
                            munitions_cost=0,
                            clip_size=ammo_source.clip_size,
                            max_clips=ammo_source.max_clips,
                            name=str(ammo_source.display_name),
                            type=ammo_type,
                            explosion_damage=projectile.properties.explosion_damage,
                            explosion_radius=projectile.properties.explosion_radius,
                        ),
                    )
            elif isinstance(weapon, HLLArmorWeaponReconGun):
                for ammo_source in ammo_sources:
                    weapon_data.ammo.append(
                        VehicleWeaponAmmo(
                            munitions_cost=0,
                            clip_size=ammo_source.clip_size,
                            max_clips=ammo_source.max_clips,
                            name=str(ammo_source.display_name),
                            type=VehicleWeaponAmmoType.RECON,
                            explosion_damage=0,
                            explosion_radius=0,
                        ),
                    )
            elif isinstance(weapon, HLLArmorWeaponSmokeScreen):
                ammo_source = weapon.properties.ammo_info.ammo_sources[0]
                weapon_data.ammo.append(
                    VehicleWeaponAmmo(
                        munitions_cost=0,
                        clip_size=ammo_source.clip_size,
                        max_clips=ammo_source.max_clips,
                        name=str(ammo_source.display_name),
                        type=VehicleWeaponAmmoType.SMOKE,
                        explosion_damage=0,
                        explosion_radius=0,
                    ),
                )
            else:
                logger.warning(
                    "Unexpected weapon type %s for weapon %s",
                    type(weapon),
                    weapon,
                )

        return VehicleData(
            blueprint_ids={self.vehicle.name.removeprefix("Default__")},
            id=str(meta_data.display_name),
            name=str(meta_data.display_name),
            type=self.vehicle_type,
            factions=self.factions,
            hull=VehicleCompartmentData(
                health=health.properties.armor_info.hull_max_health or 0,
            ),
            turret=VehicleCompartmentData(
                health=health.properties.armor_info.turret_max_health or 0,
            ),
            tracks=VehicleCompartmentData(
                health=health.properties.armor_info.tracks_max_health or 0,
            ),
            engine=VehicleCompartmentData(
                health=health.properties.armor_info.engine_max_health or 0,
            ),
            seats=seats,
        )


class InfantryVehicleExtractor(
    VehicleExtractor[HLLTruckProperties | HLLHalftrackProperties],
):
    def get_weapon_type(self, weapon: HLLArmorWeapon, seat_index: int) -> HLLWeaponType:
        if isinstance(weapon, HLLArmorWeaponBallistic):
            return HLLWeaponType.MOUNTED_MG

        return super().get_weapon_type(weapon, seat_index)

    def extract(self) -> VehicleData:
        meta_data = self.vehicle.properties.armor_meta_data
        health = self.vehicle.properties.armor_health.get(HLLArmorHealthComponent)
        inventory = self.vehicle.properties.armor_inventory.get(HLLArmorInventory)

        driver_seat = self.vehicle.properties.get_driver_seat()
        front_passenger_seat = self.vehicle.properties.get_front_passenger_seat()
        back_passenger_seat = self.vehicle.properties.get_back_passenger_seat()

        seats = [
            self.seat_component_to_model(driver_seat),
            self.seat_component_to_model(front_passenger_seat),
        ]
        seats.extend(
            self.seat_component_to_model(back_passenger_seat)
            for _ in range(self.vehicle.properties.num_back_passenger_seats)
        )

        for inventory_item in inventory.properties.default_inventory:
            seat_index = inventory_item.owning_seat_index
            weapon = inventory_item.get_weapon()
            weapon_type = self.get_weapon_type(weapon, seat_index)

            weapon_data = VehicleWeapon(
                name=str(weapon.properties.weapon_name),
                type=weapon_type,
                ammo=[],
            )
            seats[seat_index].weapons.append(weapon_data)

        return VehicleData(
            blueprint_ids={self.vehicle.name.removeprefix("Default__")},
            id=str(meta_data.display_name),
            name=str(meta_data.display_name),
            type=self.vehicle_type,
            factions=self.factions,
            hull=VehicleCompartmentData(
                health=health.properties.armor_info.hull_max_health or 0,
            ),
            turret=VehicleCompartmentData(
                health=health.properties.armor_info.turret_max_health or 0,
            ),
            tracks=VehicleCompartmentData(
                health=health.properties.armor_info.tracks_max_health or 0,
            ),
            engine=VehicleCompartmentData(
                health=health.properties.armor_info.engine_max_health or 0,
            ),
            seats=seats,
        )


ABILITIES_DIR = Path("HLL/Content/Blueprints/Abilities/Setup")
ABILITIES_FACTIONS: dict[Path, HLLFaction | None] = {
    ABILITIES_DIR / "US_DefaultAbilities": HLLFaction.US,
    ABILITIES_DIR / "US_DefaultAbilities_Winter": HLLFaction.US,
    ABILITIES_DIR / "GER_DefaultAbilities": HLLFaction.GER,
    ABILITIES_DIR / "GER_DefaultAbilities_Winter": HLLFaction.GER,
    ABILITIES_DIR / "GER_DefaultAbilities_STA": HLLFaction.GER,
    ABILITIES_DIR / "RU_DefaultAbilities": HLLFaction.RUS,
    ABILITIES_DIR / "RU_DefaultAbilities_Winter": HLLFaction.RUS,
    ABILITIES_DIR / "COM_DefaultAbilities": HLLFaction.CW,
    ABILITIES_DIR / "NA_Variant/GER_DefaultAbilities_NA": HLLFaction.DAK,
    ABILITIES_DIR / "NA_Variant/COM_DefaultAbilities_NA": HLLFaction.B8A,
}
ABILITIES_FACTIONS = {
    local_to_abs_path(fp): faction for fp, faction in ABILITIES_FACTIONS.items()
}


def get_all_ability_files() -> Iterator[Path]:
    abilities_dir = local_to_abs_path(ABILITIES_DIR, add_ext=False)
    yield from abilities_dir.glob("**/*_DefaultAbilities*.json")


def get_all_ability_tables() -> Iterator[tuple[HLLMapAbilityData, HLLFaction]]:
    for ability_fp in get_all_ability_files():
        ability_data = load_object_from_file(ability_fp, 0, HLLMapAbilityData)
        faction = ABILITIES_FACTIONS.get(ability_fp)
        if faction is None:
            if ability_fp not in ABILITIES_FACTIONS:
                logger.warning(
                    "Ability file %s not found in ABILITIES_FACTIONS mapping",
                    ability_fp,
                )
            continue
        yield ability_data, faction


def get_all_abilities() -> Iterator[tuple[HLLCommanderAbility, HLLFaction]]:
    for ability_table, faction in get_all_ability_tables():
        for ability in ability_table.properties.abilities:
            if a := ability.get_ability():
                yield a, faction


UI_SUBCATEGORY_TO_VEHICLE_TYPE: dict[str, VehicleType] = {
    "HEAVY ARMOR": HLLVehicleType.HEAVY_TANK,
    "MEDIUM ARMOR": HLLVehicleType.MEDIUM_TANK,
    "LIGHT ARMOR": HLLVehicleType.LIGHT_TANK,
    "RECON": HLLVehicleType.RECON_VEHICLE,
    "SELF-PROPELLED ARTILLERY": HLLVehicleType.SELF_PROPELLED_ARTILLERY,
    "HALF-TRACK": HLLVehicleType.HALF_TRACK,
    "SUPPORT": HLLVehicleType.SUPPLY_TRUCK,
}


def get_vehicle_type_from_ui_subcategory(
    vehicle_bgc: BlueprintGeneratedClass[HLLVehicle],
    ui_sub_category: str,
) -> VehicleType:
    vehicle_type = UI_SUBCATEGORY_TO_VEHICLE_TYPE[ui_sub_category]
    if vehicle_type != HLLVehicleType.SUPPLY_TRUCK:
        return vehicle_type

    vehicle_struct = vehicle_bgc.get_root_struct_name()
    if vehicle_struct == "Class'BaseJeep'":
        return HLLVehicleType.JEEP
    if vehicle_struct == "Class'BaseTruck'":
        if "transport" in vehicle_bgc.name.lower():
            return HLLVehicleType.TRANSPORT_TRUCK
        if "supply" in vehicle_bgc.name.lower():
            return HLLVehicleType.SUPPLY_TRUCK
        msg = (
            "Cannot determine vehicle type for BaseTruck with name"
            f" '{vehicle_bgc.name}'"
        )
        raise ValueError(msg)
    msg = f"Unexpected vehicle struct '{vehicle_struct}'"
    raise ValueError(msg)


STRUCT_NAME_TO_VEHICLE_CLASS: dict[str, type[HLLVehicle]] = {
    "Class'Daimler'": HLLVehicle[HLLArmorProperties],
    "Class'T70'": HLLVehicle[HLLArmorProperties],
    "Class'Luchs'": HLLVehicle[HLLArmorProperties],
    "Class'BaseJeep'": HLLVehicle[HLLTruckProperties],
    "Class'Greyhound'": HLLVehicle[HLLArmorProperties],
    "Class'Puma'": HLLVehicle[HLLArmorProperties],
    "Class'Panther'": HLLVehicle[HLLArmorProperties],
    "Class'BA10'": HLLVehicle[HLLArmorProperties],
    "Class'T34'": HLLVehicle[HLLArmorProperties],
    "Class'ShermanJumbo'": HLLVehicle[HLLArmorProperties],
    "Class'M3Halftrack'": HLLVehicle[HLLHalftrackProperties],
    "Class'BaseTruck'": HLLVehicle[HLLTruckProperties],
    "Class'SelfPropelledArtillery'": HLLVehicle[HLLSelfPropelledArtilleryProperties],
    "Class'Tiger'": HLLVehicle[HLLArmorProperties],
    "Class'SdKfz251Halftrack'": HLLVehicle[HLLHalftrackProperties],
}


def get_vehicle_class_from_root_struct(
    vehicle_bgc: BlueprintGeneratedClass[HLLVehicle],
) -> type[HLLVehicle]:
    struct_name = vehicle_bgc.get_root_struct_name()
    if struct_name not in STRUCT_NAME_TO_VEHICLE_CLASS:
        msg = f"Unexpected vehicle struct '{struct_name}' for vehicle {vehicle_bgc}"
        raise ValueError(msg)
    return STRUCT_NAME_TO_VEHICLE_CLASS[struct_name]


def get_all_vehicles() -> Iterator[tuple[HLLVehicle, VehicleType, set[HLLFaction]]]:
    seen: dict[HLLVehicle, tuple[VehicleType, set[HLLFaction]]] = {}

    for ability, faction in get_all_abilities():
        if not isinstance(
            ability.properties,
            HLLCommanderAbilitySpawnVehicleProperties,
        ):
            continue

        vehicle_bgc = ability.properties.vehicle_class.get(
            BlueprintGeneratedClass[HLLVehicle],
        )
        vehicle_cls = get_vehicle_class_from_root_struct(vehicle_bgc)
        vehicle = vehicle_bgc.get_default_object(vehicle_cls)
        vehicle_type = get_vehicle_type_from_ui_subcategory(
            vehicle_bgc,
            str(ability.properties.ui_sub_category),
        )

        if vehicle in seen:
            if seen[vehicle][0] != vehicle_type:
                logger.error(
                    "Vehicle %s has inconsistent types: %s and %s",
                    vehicle,
                    seen[vehicle][0],
                    vehicle_type,
                )
            seen[vehicle][1].add(faction)
            continue

        seen[vehicle] = (vehicle_type, {faction})

    for vehicle, (vehicle_type, factions) in seen.items():
        yield vehicle, vehicle_type, factions


def get_all_vehicle_data() -> Iterator[VehicleData]:
    for vehicle, vehicle_type, factions in get_all_vehicles():
        if isinstance(vehicle.properties, HLLArmorProperties):
            data = ArmoredVehicleExtractor(
                cast("HLLVehicle[HLLArmorProperties]", vehicle),
                vehicle_type,
                factions,
            ).extract()

        elif isinstance(
            vehicle.properties,
            (HLLHalftrackProperties, HLLTruckProperties),
        ):
            data = InfantryVehicleExtractor(
                cast(
                    "HLLVehicle[HLLHalftrackProperties | HLLTruckProperties]",
                    vehicle,
                ),
                vehicle_type,
                factions,
            ).extract()

        else:
            msg = (
                f"Unexpected vehicle properties type {type(vehicle.properties)}"
                f"for vehicle {vehicle}"
            )
            raise TypeError(msg)

        yield data


def main() -> None:
    vehicle_data = sorted(get_all_vehicle_data(), key=lambda v: v.id)
    vehicle_ids = itertools.groupby(vehicle_data, lambda v: v.id)
    vehicles = [VehicleData.merge(*vd_seq) for _, vd_seq in vehicle_ids]
    vehicle_constructors: list[str] = [v.to_constructor() for v in vehicles]

    inject_code(
        Path("hllrcon/data/vehicles.py"),
        "hll vehicles",
        "\n\n".join(vehicle_constructors),
    )

    Path("dist").mkdir(exist_ok=True)
    Path("dist/vehicles.json").write_bytes(
        TypeAdapter(list[VehicleData]).dump_json(vehicles, indent=2),
    )

    weapon_data = sorted(
        (
            weapon
            for vehicle in vehicles
            for weapon in vehicle.get_weapons(include_generic=True)
        ),
        key=lambda w: w.id,
    )
    weapon_ids = itertools.groupby(weapon_data, lambda w: w.id)
    weapons = [WeaponData.merge(*wd_seq) for _, wd_seq in weapon_ids]
    weapon_constructors: list[str] = [w.to_constructor() for w in weapons]

    inject_code(
        Path("hllrcon/data/weapons.py"),
        "hll vehicles",
        "\n\n".join(weapon_constructors),
    )


if __name__ == "__main__":
    main()
