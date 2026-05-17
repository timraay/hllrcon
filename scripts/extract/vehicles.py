import itertools
import logging
from abc import ABC, abstractmethod
from collections.abc import Iterator
from enum import StrEnum
from pathlib import Path
from typing import Generic, TypedDict, cast

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
from scripts.extractlib.objects.hll_armor_inventory import (
    HLLArmorInventory,
    HLLArmorInventoryPropertiesDefaultInventoryItem,
)
from scripts.extractlib.objects.hll_armor_weapon import (
    EShellType,
    HLLArmorWeapon,
    HLLArmorWeaponBallistic,
    HLLArmorWeaponHowitzer,
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
    HLLAntiTankGunProperties,
    HLLArmorProperties,
    HLLHalftrackProperties,
    HLLHowitzerProperties,
    HLLReconVehicleProperties,
    HLLSelfPropelledArtilleryProperties,
    HLLTruckProperties,
    HLLVehicle,
    HLLVehiclePropT_co,
)
from scripts.extractlib.objects.tank_seat import VehicleSeat
from scripts.extractlib.utils import find_objects_in_dir

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

HLL_VEHICLE_SEAT_CONSTRUCTOR_TEMPLATE = """\
HLLVehicleSeat(
    index={index},
    type=HLLVehicleSeatType.{seat.name},
    weapons={weapons},
    requires_roles={requires_roles},
    exposed={exposed},
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
        if shell_type in (EShellType.SMOKE, EShellType.MAX):
            return cls.SMOKE
        return None

    def is_lethal(self) -> bool:
        return self not in (VehicleWeaponAmmoType.RECON, VehicleWeaponAmmoType.SMOKE)


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

    def is_lethal(self) -> bool:
        return any(ammo.type.is_lethal() for ammo in self.ammo)


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
            meth_name = "V_" + to_method_name(weapon_id).lstrip("_")
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
            if include_generic and weapon.is_lethal():
                generic_meth_name = (
                    "V_" + to_method_name(weapon.name).lstrip("_") + "__UNKNOWN"
                )
                weapons.append(
                    WeaponData(
                        meth_name=generic_meth_name,
                        id=weapon.name,
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


_vehicle_id_no_metadata_warned: set[str] = set()


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
    exposed: bool = False

    @model_validator(mode="after")
    def set_meth_name(self) -> "VehicleData":
        meta = HLL_VEHICLE_METADATA.get(self.id)
        if meta is not None:
            self.meth_name = meta.get("meth_name", self.meth_name)
            self.name = meta.get("name", self.name)
            self.exposed = meta.get("exposed", self.exposed)
        elif self.id not in _vehicle_id_no_metadata_warned:
            logger.warning("No metadata found for vehicle ID: %s", self.id)
            _vehicle_id_no_metadata_warned.add(self.id)

        if not self.meth_name:
            self.meth_name = to_method_name(self.id)
        return self

    def get_weapons(self, *, include_generic: bool = False) -> list[WeaponData]:
        weapons: list[WeaponData] = []
        if self.type not in (HLLVehicleType.ARTILLERY, HLLVehicleType.ANTI_TANK_GUN):
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
                    exposed=self.exposed,
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

    def _get_weapon_ammo_ballistic(
        self,
        weapon_data: VehicleWeapon,
        weapon: HLLArmorWeaponBallistic,
    ) -> None:
        ammo_sources = weapon.properties.ammo_info.ammo_sources
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

    def _get_weapon_ammo_projectile(
        self,
        weapon_data: VehicleWeapon,
        weapon: HLLArmorWeaponProjectile,
    ) -> None:
        ammo_sources = weapon.properties.ammo_info.ammo_sources
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
                ammo_type = VehicleWeaponAmmoType.AP
                if weapon_data.type != HLLWeaponType.AT_GUN:
                    logger.error(
                        "Cannot determine ammo type for source %s",
                        ammo_source,
                    )

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

    def _get_weapon_ammo_howitzer(
        self,
        weapon_data: VehicleWeapon,
        weapon: HLLArmorWeaponHowitzer,
    ) -> None:
        ammo_sources = weapon.properties.ammo_info.ammo_sources
        projectiles = weapon.get_projectiles()
        for ammo_source, projectile in zip(
            ammo_sources,
            projectiles,
            strict=True,
        ):
            if projectile.properties.damage == 0:
                ammo_type = VehicleWeaponAmmoType.SMOKE
            else:
                ammo_type = VehicleWeaponAmmoType.HE

            weapon_data.ammo.append(
                VehicleWeaponAmmo(
                    munitions_cost=0,
                    clip_size=ammo_source.clip_size,
                    max_clips=ammo_source.max_clips,
                    name=str(ammo_source.display_name),
                    type=ammo_type,
                    explosion_damage=projectile.properties.damage,
                    explosion_radius=projectile.properties.damage_radius,
                ),
            )

    def _get_weapon_ammo_mounted_howitzer(
        self,
        weapon_data: VehicleWeapon,
        weapon: HLLArmorWeaponMountedHowitzer,
    ) -> None:
        ammo_sources = weapon.properties.ammo_info.ammo_sources
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

    def _get_weapon_ammo_recon_gun(
        self,
        weapon_data: VehicleWeapon,
        weapon: HLLArmorWeaponReconGun,
    ) -> None:
        ammo_sources = weapon.properties.ammo_info.ammo_sources
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

    def _get_weapon_ammo_smoke_screen(
        self,
        weapon_data: VehicleWeapon,
        weapon: HLLArmorWeaponSmokeScreen,
    ) -> None:
        ammo_sources = weapon.properties.ammo_info.ammo_sources
        for ammo_source in ammo_sources:
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

    def get_weapon(
        self,
        inventory_item: HLLArmorInventoryPropertiesDefaultInventoryItem,
    ) -> VehicleWeapon:
        seat_index = inventory_item.owning_seat_index
        weapon = inventory_item.get_weapon()
        weapon_type = self.get_weapon_type(weapon, seat_index)

        weapon_data = VehicleWeapon(
            name=str(weapon.properties.weapon_name),
            type=weapon_type,
            ammo=[],
        )

        if isinstance(weapon, HLLArmorWeaponBallistic):
            self._get_weapon_ammo_ballistic(weapon_data, weapon)
        elif isinstance(
            weapon,
            HLLArmorWeaponProjectile,
        ):
            self._get_weapon_ammo_projectile(weapon_data, weapon)
        elif isinstance(
            weapon,
            HLLArmorWeaponHowitzer,
        ):
            self._get_weapon_ammo_howitzer(weapon_data, weapon)
        elif isinstance(
            weapon,
            HLLArmorWeaponMountedHowitzer,
        ):
            self._get_weapon_ammo_mounted_howitzer(weapon_data, weapon)
        elif isinstance(weapon, HLLArmorWeaponReconGun):
            self._get_weapon_ammo_recon_gun(weapon_data, weapon)
        elif isinstance(weapon, HLLArmorWeaponSmokeScreen):
            self._get_weapon_ammo_smoke_screen(weapon_data, weapon)
        else:
            logger.warning(
                "Unexpected weapon type %s for weapon %s",
                type(weapon),
                weapon,
            )

        return weapon_data

    @abstractmethod
    def extract(self) -> VehicleData: ...


class ArmoredVehicleExtractor(
    VehicleExtractor[
        HLLArmorProperties
        | HLLReconVehicleProperties
        | HLLSelfPropelledArtilleryProperties
    ],
):
    def get_weapon_type(self, weapon: HLLArmorWeapon, seat_index: int) -> HLLWeaponType:
        if isinstance(weapon, HLLArmorWeaponBallistic):
            if seat_index == 0:
                return HLLWeaponType.TANK_HULL_MG
            return HLLWeaponType.TANK_COAXIAL_MG

        if isinstance(weapon, HLLArmorWeaponProjectile | HLLArmorWeaponMountedHowitzer):
            return HLLWeaponType.TANK_CANNON

        if isinstance(weapon, HLLArmorWeaponReconGun):
            return HLLWeaponType.TANK_RECON

        if isinstance(weapon, HLLArmorWeaponSmokeScreen):
            return HLLWeaponType.TANK_SMOKE_SCREEN

        return super().get_weapon_type(weapon, seat_index)

    def extract(self) -> VehicleData:
        meta_data = self.vehicle.properties.armor_meta_data
        health = self.vehicle.properties.armor_health.get(HLLArmorHealthComponent)
        inventory = self.vehicle.properties.armor_inventory.get(HLLArmorInventory)

        seats = [
            self.seat_component_to_model(seat)
            for seat in self.vehicle.properties.get_seats()
        ]

        for inventory_item in inventory.properties.default_inventory:
            weapon_data = self.get_weapon(inventory_item)

            seat_index = inventory_item.owning_seat_index
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


class ArtilleryVehicleExtractor(
    VehicleExtractor[HLLHowitzerProperties | HLLAntiTankGunProperties],
):
    def get_weapon_type(self, weapon: HLLArmorWeapon, seat_index: int) -> HLLWeaponType:  # noqa: ARG002
        if isinstance(weapon, HLLArmorWeaponHowitzer):
            return HLLWeaponType.ARTILLERY
        return HLLWeaponType.AT_GUN

    def extract(self) -> VehicleData:
        meta_data = self.vehicle.properties.armor_meta_data
        health = self.vehicle.properties.armor_health.get(HLLArmorHealthComponent)
        inventory = self.vehicle.properties.armor_inventory.get(HLLArmorInventory)

        seats = [
            self.seat_component_to_model(seat)
            for seat in self.vehicle.properties.get_seats()
        ]

        for inventory_item in inventory.properties.default_inventory:
            weapon_data = self.get_weapon(inventory_item)
            seat_index = inventory_item.owning_seat_index
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

        seats = [
            self.seat_component_to_model(seat)
            for seat in self.vehicle.properties.get_seats()
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
ABILITIES_FACTIONS: dict[Path, set[HLLFaction]] = {
    ABILITIES_DIR / "US_DefaultAbilities": {HLLFaction.US},
    ABILITIES_DIR / "US_DefaultAbilities_Winter": {HLLFaction.US},
    ABILITIES_DIR / "GER_DefaultAbilities": {HLLFaction.GER},
    ABILITIES_DIR / "GER_DefaultAbilities_Winter": {HLLFaction.GER},
    ABILITIES_DIR / "GER_DefaultAbilities_STA": {HLLFaction.GER},
    ABILITIES_DIR / "RU_DefaultAbilities": {HLLFaction.RUS},
    ABILITIES_DIR / "RU_DefaultAbilities_Winter": {HLLFaction.RUS},
    ABILITIES_DIR / "COM_DefaultAbilities": {HLLFaction.CW},
    ABILITIES_DIR / "NA_Variant/GER_DefaultAbilities_NA": {HLLFaction.DAK},
    ABILITIES_DIR / "NA_Variant/COM_DefaultAbilities_NA": {HLLFaction.B8A},
}
ABILITIES_FACTIONS = {
    local_to_abs_path(fp): factions for fp, factions in ABILITIES_FACTIONS.items()
}


ARTILLERY_DIR = Path("HLL/Content/Blueprints/Artillery")
ARTILLERY_FACTIONS: dict[Path, set[HLLFaction]] = {
    ARTILLERY_DIR / "US/Anti-Tank/BP_USAntiTank": {HLLFaction.US},
    ARTILLERY_DIR / "RUS/Anti-Tank/BP_RUSAntiTank": {HLLFaction.RUS},
    ARTILLERY_DIR / "GER/Anti-Tank/BP_GERAntiTank": {HLLFaction.GER, HLLFaction.DAK},
    ARTILLERY_DIR / "COM/Anti-Tank/BP_COMAntiTank": {HLLFaction.CW, HLLFaction.B8A},
    ARTILLERY_DIR / "US/Howitzer/BP_US_M114": {HLLFaction.US},
    ARTILLERY_DIR / "RUS/Artillery/BP_RUS_M30": {HLLFaction.RUS},
    ARTILLERY_DIR / "GER/Howitzer/BP_GER_SFH18": {HLLFaction.GER, HLLFaction.DAK},
    ARTILLERY_DIR / "COM/Howitzer/BP_COM_Howitzer": {HLLFaction.CW, HLLFaction.B8A},
}
ARTILLERY_FACTIONS = {
    local_to_abs_path(fp): factions for fp, factions in ARTILLERY_FACTIONS.items()
}


def get_all_ability_files() -> Iterator[Path]:
    abilities_dir = local_to_abs_path(ABILITIES_DIR, add_ext=False)
    yield from abilities_dir.glob("**/*_DefaultAbilities*.json")


def get_all_ability_tables() -> Iterator[tuple[HLLMapAbilityData, set[HLLFaction]]]:
    for ability_fp in get_all_ability_files():
        ability_data = load_object_from_file(ability_fp, 0, HLLMapAbilityData)
        factions = ABILITIES_FACTIONS.get(ability_fp)
        if not factions:
            if factions is None:
                logger.warning(
                    "Ability file %s not found in ABILITIES_FACTIONS mapping",
                    ability_fp,
                )
            continue
        yield ability_data, factions


def get_all_abilities() -> Iterator[tuple[HLLCommanderAbility, set[HLLFaction]]]:
    for ability_table, factions in get_all_ability_tables():
        for ability in ability_table.properties.abilities:
            if a := ability.get_ability():
                yield a, factions


def get_all_artillery() -> Iterator[tuple[HLLVehicle, Path]]:
    for howitzer_bgc, fp in find_objects_in_dir(
        local_to_abs_path(ARTILLERY_DIR, add_ext=False),
        lambda bgc: bgc.get_root_struct_name() == "Class'HLLHowitzer'",
        obj_type=BlueprintGeneratedClass[HLLVehicle[HLLHowitzerProperties]],
        glob_pattern="**/BP_*.json",
        cond_obj_type=BlueprintGeneratedClass,
    ):
        yield howitzer_bgc.get_default_object(HLLVehicle[HLLHowitzerProperties]), fp

    for antitank_bgc, fp in find_objects_in_dir(
        local_to_abs_path(ARTILLERY_DIR, add_ext=False),
        lambda bgc: bgc.get_root_struct_name() == "Class'HLLAntiTankGun'",
        obj_type=BlueprintGeneratedClass[HLLVehicle[HLLAntiTankGunProperties]],
        glob_pattern="**/BP_*.json",
        cond_obj_type=BlueprintGeneratedClass,
    ):
        yield antitank_bgc.get_default_object(HLLVehicle[HLLAntiTankGunProperties]), fp


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
    "Class'Daimler'": HLLVehicle[HLLReconVehicleProperties],
    "Class'T70'": HLLVehicle[HLLArmorProperties],
    "Class'Luchs'": HLLVehicle[HLLArmorProperties],
    "Class'BaseJeep'": HLLVehicle[HLLTruckProperties],
    "Class'Greyhound'": HLLVehicle[HLLReconVehicleProperties],
    "Class'Puma'": HLLVehicle[HLLReconVehicleProperties],
    "Class'Panther'": HLLVehicle[HLLArmorProperties],
    "Class'BA10'": HLLVehicle[HLLReconVehicleProperties],
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


def _get_all_vehicles() -> Iterator[tuple[HLLVehicle, VehicleType, set[HLLFaction]]]:
    for ability, factions in get_all_abilities():
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

        yield vehicle, vehicle_type, factions

    for vehicle, vehicle_fp in get_all_artillery():
        if vehicle_fp not in ARTILLERY_FACTIONS:
            logger.warning(
                "Artillery file %s not found in ARTILLERY_FACTIONS mapping",
                vehicle_fp,
            )
            continue

        if not ARTILLERY_FACTIONS[vehicle_fp]:
            continue

        factions = ARTILLERY_FACTIONS[vehicle_fp]
        yield vehicle, HLLVehicleType.ARTILLERY, factions


def get_all_vehicles() -> Iterator[tuple[HLLVehicle, VehicleType, set[HLLFaction]]]:
    seen: dict[HLLVehicle, tuple[VehicleType, set[HLLFaction]]] = {}

    for vehicle, vehicle_type, factions in _get_all_vehicles():
        if vehicle in seen:
            if seen[vehicle][0] != vehicle_type:
                logger.error(
                    "Vehicle %s has inconsistent types: %s and %s",
                    vehicle,
                    seen[vehicle][0],
                    vehicle_type,
                )
            seen[vehicle][1].update(factions)
            continue

        seen[vehicle] = (vehicle_type, factions)

    for vehicle, (vehicle_type, factions) in seen.items():
        yield vehicle, vehicle_type, factions


def get_all_vehicle_data() -> Iterator[VehicleData]:
    for vehicle, vehicle_type, factions in get_all_vehicles():
        if isinstance(vehicle.properties, HLLArmorProperties):
            data = ArmoredVehicleExtractor(
                cast(
                    "HLLVehicle[HLLArmorProperties | HLLReconVehicleProperties]",
                    vehicle,
                ),
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
        elif isinstance(
            vehicle.properties,
            (HLLHowitzerProperties, HLLAntiTankGunProperties),
        ):
            data = ArtilleryVehicleExtractor(
                cast(
                    "HLLVehicle[HLLHowitzerProperties | HLLAntiTankGunProperties]",
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


class VehicleMetaData(TypedDict, total=False):
    meth_name: str
    name: str
    exposed: bool


HLL_VEHICLE_METADATA: dict[str, VehicleMetaData] = {
    "Daimler": {
        "name": "Daimler",
        "exposed": False,
    },
    "Tetrarch": {
        "name": "Tetrarch",
        "exposed": False,
    },
    "Jeep Willys": {
        "name": "Willy's Jeep",
        "exposed": True,
    },
    "Firefly": {
        "name": "Sherman Firefly",
        "exposed": False,
    },
    "Bedford OYD (Supply)": {
        "name": "Bedford OYD",
        "exposed": True,
    },
    "Bedford OYD (Transport)": {
        "name": "Bedford OYD",
        "exposed": True,
    },
    "M3 Half-track": {
        "name": "M3 Half-track",
        "exposed": True,
    },
    "Cromwell": {
        "name": "Cromwell",
        "exposed": False,
    },
    "Churchill Mk.VII": {
        "name": "Churchill Mk VII",
        "exposed": False,
    },
    "Churchill Mk III A.V.R.E.": {
        "meth_name": "CHURCHILL_MK_III_AVRE",
        "name": "Churchill AVRE",
        "exposed": False,
    },
    "Sd.Kfz.234 Puma": {
        "name": "Sd.Kfz.234 Puma",
        "exposed": False,
    },
    "Sd.Kfz.171 Panther": {
        "name": "Sd.Kfz.171 Panther",
        "exposed": False,
    },
    "Sd.Kfz.181 Tiger 1": {
        "name": "Sd.Kfz.181 Tiger 1",
        "exposed": False,
    },
    "Sturmpanzer IV": {
        "name": "Sturmpanzer IV",
        "exposed": False,
    },
    "Opel Blitz (Supply)": {
        "name": "Opel Blitz",
        "exposed": True,
    },
    "Opel Blitz (Transport)": {
        "name": "Opel Blitz",
        "exposed": True,
    },
    "Sd.Kfz 251 Half-track": {
        "name": "Sd.Kfz.251 Half-track",
        "exposed": True,
    },
    "Sd.Kfz.121 Luchs": {
        "name": "Sd.Kfz.121 Luchs",
        "exposed": False,
    },
    "Sd.Kfz.161 Panzer IV": {
        "name": "Sd.Kfz.161 Panzer IV",
        "exposed": False,
    },
    "Kubelwagen": {
        "name": "Kubelwagen",
        "exposed": True,
    },
    "BA-10": {
        "name": "BA-10",
        "exposed": False,
    },
    "T34/76": {
        "name": "T34/76",
        "exposed": False,
    },
    "IS-1": {
        "name": "IS-1",
        "exposed": False,
    },
    "ZIS-5 (Supply)": {
        "name": "ZIS-5",
        "exposed": True,
    },
    "ZIS-5 (Transport)": {
        "name": "ZIS-5",
        "exposed": True,
    },
    "GAZ-67": {
        "name": "GAZ-67",
        "exposed": True,
    },
    "T70": {
        "name": "T70",
        "exposed": False,
    },
    "KV-2": {
        "name": "KV-2",
        "exposed": False,
    },
    "M8 Greyhound": {
        "name": "M8 Greyhound",
        "exposed": False,
    },
    "Sherman M4A3E2": {
        "name": "M4A3E2 Sherman",
        "exposed": False,
    },
    "Sherman M4A3E2(76)": {
        "name": "M4A3E2(76) Sherman",
        "exposed": False,
    },
    "GMC CCKW 353 (Supply)": {
        "name": "GMC CCKW 353",
        "exposed": True,
    },
    "GMC CCKW 353 (Transport)": {
        "name": "GMC CCKW 353",
        "exposed": True,
    },
    "Sherman M4A3(75)W": {
        "name": "M4A3(75)W Sherman",
        "exposed": False,
    },
    "Stuart M5A1": {
        "name": "M5A1 Stuart",
        "exposed": False,
    },
    "M4A3 (105mm)": {
        "name": "Sherman M4(104)",
        "exposed": False,
    },
    "M3 Stuart Honey": {
        "name": "M3 Stuart Honey",
        "exposed": False,
    },
    "Churchill Mk.III": {
        "name": "Churchill Mk III",
        "exposed": False,
    },
    "Crusader Mk.III": {
        "name": "Crusader Mk III",
        "exposed": False,
    },
    "Bishop SP 25pdr": {
        "name": "Bishop",
        "exposed": False,
    },
    "Panzer III Ausf.N": {
        "name": "Sd.Kfz.141 Panzer III",
        "exposed": False,
    },
    "M114": {
        "name": "M114 Howitzer",
        "exposed": True,
    },
    "M1938 (M-30)": {
        "name": "M-30",
        "exposed": True,
    },
    "sFH 18": {
        "name": "sFH 18",
        "exposed": True,
    },
    "QF 25-Pounder": {
        "name": "QF 25-Pounder",
        "exposed": True,
    },
    "M1 57mm": {
        "name": "M1 57mm",
        "exposed": True,
    },
    "ZiS-2": {
        "name": "ZiS-2",
        "exposed": True,
    },
    "PAK 40": {
        "name": "Pak 40",
        "exposed": True,
    },
    "QF 6-Pounder": {
        "name": "QF 6-Pounder",
        "exposed": True,
    },
}


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
