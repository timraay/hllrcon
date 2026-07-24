import itertools
import logging
from abc import ABC, abstractmethod
from collections.abc import Iterator
from enum import StrEnum
from pathlib import Path
from typing import Generic, TypedDict, cast

from pydantic import BaseModel, TypeAdapter, model_validator

from hllrcon.data.factions import AnyFaction, HLLFaction, HLLVFaction
from hllrcon.data.vehicles import VehicleSeatType, VehicleType
from hllrcon.data.weapons import WeaponType
from scripts import HLL_METADATA_PATH, HLLV_METADATA_PATH
from scripts.extract.utils import (
    inject_code,
    stringify_enum_member,
    stringify_factions,
    stringify_list,
    to_method_name,
)
from scripts.extract.weapons import WeaponData
from scripts.extractlib.loader import (
    get_root_path,
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
    HLLArmorWeaponGrenade,
    HLLArmorWeaponHowitzer,
    HLLArmorWeaponMortar,
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
    HLLAntiAircraftGunProperties,
    HLLAntiTankGunProperties,
    HLLArmorProperties,
    HLLHalftrackProperties,
    HLLHowitzerProperties,
    HLLMortarProperties,
    HLLReconVehicleProperties,
    HLLSelfPropelledArtilleryProperties,
    HLLTruckProperties,
    HLLVBoatProperties,
    HLLVehicle,
    HLLVehiclePropT_co,
    HLLVHelicopterProperties,
)
from scripts.extractlib.objects.shooter_projectile import ShooterProjectile
from scripts.extractlib.objects.tank_seat import VehicleSeat
from scripts.extractlib.utils import find_objects_in_dir, game_switch, root_path_ctx

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
            type=VehicleType.{vehicle.type.name},
            seats={seats},
        )"""

HLL_VEHICLE_SEAT_CONSTRUCTOR_TEMPLATE = """\
HLLVehicleSeat(
    index={index},
    type={type},
    weapons={weapons},
    requires_roles={requires_roles},
    exposed={exposed},
)"""
HLLV_VEHICLE_CONSTRUCTOR_TEMPLATE = """\
    @class_cached_property
    @classmethod
    def {vehicle.meth_name}(cls) -> "HLLVVehicle":
        \"\"\"*{vehicle.id}*\"\"\"
        return cls(
            id="{vehicle.id}",
            name="{vehicle.name}",
            factions={factions},
            type=VehicleType.{vehicle.type.name},
            seats={seats},
        )"""

HLLV_VEHICLE_SEAT_CONSTRUCTOR_TEMPLATE = """\
HLLVVehicleSeat(
    index={index},
    type={type},
    weapons={weapons},
    requires_roles={requires_roles},
    exposed={exposed},
)"""

with root_path_ctx(HLL_METADATA_PATH):
    HLL_ABILITIES_DIR = Path("HLL/Content/Blueprints/Abilities/Setup")
    HLL_ABILITIES_FACTIONS: dict[Path, set[AnyFaction]] = {
        HLL_ABILITIES_DIR / "US_DefaultAbilities": {HLLFaction.US},
        HLL_ABILITIES_DIR / "US_DefaultAbilities_Winter": {HLLFaction.US},
        HLL_ABILITIES_DIR / "GER_DefaultAbilities": {HLLFaction.GER},
        HLL_ABILITIES_DIR / "GER_DefaultAbilities_Winter": {HLLFaction.GER},
        HLL_ABILITIES_DIR / "GER_DefaultAbilities_STA": {HLLFaction.GER},
        HLL_ABILITIES_DIR / "RU_DefaultAbilities": {HLLFaction.RUS},
        HLL_ABILITIES_DIR / "RU_DefaultAbilities_Winter": {HLLFaction.RUS},
        HLL_ABILITIES_DIR / "COM_DefaultAbilities": {HLLFaction.CW},
        HLL_ABILITIES_DIR / "CAN_DefaultAbilities": {HLLFaction.CAN},
        HLL_ABILITIES_DIR / "NA_Variant/GER_DefaultAbilities_NA": {HLLFaction.DAK},
        HLL_ABILITIES_DIR / "NA_Variant/COM_DefaultAbilities_NA": {HLLFaction.B8A},
    }
    HLL_ABILITIES_FACTIONS = {
        local_to_abs_path(fp): factions
        for fp, factions in HLL_ABILITIES_FACTIONS.items()
    }

    HLL_ARTILLERY_DIR = Path("HLL/Content/Blueprints/Artillery")
    HLL_ARTILLERY_FACTIONS: dict[Path, set[AnyFaction]] = {
        HLL_ARTILLERY_DIR / "US/Anti-Tank/BP_USAntiTank": {HLLFaction.US},
        HLL_ARTILLERY_DIR / "RUS/Anti-Tank/BP_RUSAntiTank": {HLLFaction.RUS},
        HLL_ARTILLERY_DIR / "GER/Anti-Tank/BP_GERAntiTank": {
            HLLFaction.GER,
            HLLFaction.DAK,
            HLLFaction.CAN,
        },
        HLL_ARTILLERY_DIR / "COM/Anti-Tank/BP_COMAntiTank": {
            HLLFaction.CW,
            HLLFaction.B8A,
            HLLFaction.CAN,
        },
        HLL_ARTILLERY_DIR / "US/Howitzer/BP_US_M114": {HLLFaction.US},
        HLL_ARTILLERY_DIR / "RUS/Artillery/BP_RUS_M30": {HLLFaction.RUS},
        HLL_ARTILLERY_DIR / "GER/Howitzer/BP_GER_SFH18": {
            HLLFaction.GER,
            HLLFaction.DAK,
        },
        HLL_ARTILLERY_DIR / "COM/Howitzer/BP_COM_Howitzer": {
            HLLFaction.CW,
            HLLFaction.B8A,
        },
    }
    HLL_ARTILLERY_FACTIONS = {
        local_to_abs_path(fp): factions
        for fp, factions in HLL_ARTILLERY_FACTIONS.items()
    }


with root_path_ctx(HLLV_METADATA_PATH):
    HLLV_ABILITIES_DIR = Path("HLLVietnam/Content/_WFL/Blueprints/Abilities")
    HLLV_ABILITIES_FACTIONS: dict[Path, set[AnyFaction]] = {
        HLLV_ABILITIES_DIR / "US/Waterfall_US_DefaultAbilities": {HLLVFaction.US},
        HLLV_ABILITIES_DIR / "NVA/Waterfall_NVA_DefaultAbilities": {HLLVFaction.NVA},
    }
    HLLV_ABILITIES_FACTIONS = {
        local_to_abs_path(fp): factions
        for fp, factions in HLLV_ABILITIES_FACTIONS.items()
    }

    HLLV_MORTARS_DIR = Path(
        "HLLVietnam/Content/_WFL/Blueprints/Weapons/MortarPrototypes",
    )
    HLLV_ANTI_AIR_DIR = Path("HLLVietnam/Content/_WFL/Blueprints/Weapons/AntiAircraft")
    HLLV_ARTILLERY_FACTIONS: dict[Path, set[AnyFaction]] = {
        HLLV_MORTARS_DIR / "US/BP_Mortar_US_M29.json": {HLLVFaction.US},
        HLLV_MORTARS_DIR / "BP_Mortar_NVA_Type67.json": {HLLVFaction.NVA},
        HLLV_ANTI_AIR_DIR / "BP_DShKMAntiAircraftGun.json": {HLLVFaction.NVA},
    }
    HLLV_ARTILLERY_FACTIONS = {
        local_to_abs_path(fp): factions
        for fp, factions in HLLV_ARTILLERY_FACTIONS.items()
    }


class VehicleWeaponAmmoType(StrEnum):
    AP = "AP"
    HE = "HE"
    MG = "MG"
    RECON = "Recon"
    SMOKE = "Smoke"

    @classmethod
    def from_shell_type(  # noqa: PLR0911
        cls,
        shell_type: EShellType,
        projectile: ShooterProjectile,
    ) -> "VehicleWeaponAmmoType | None":
        if shell_type == EShellType.AP:
            return cls.AP
        if shell_type == EShellType.HE:
            return cls.HE
        if shell_type in (EShellType.SMOKE, EShellType.MAX):
            return cls.SMOKE

        if projectile.type in ("BP_Heavy_Shell_C", "BP_ATGun_Shell_C"):
            return cls.AP
        if projectile.type in (
            "BP_HE_Heavy_Shell_C",
            "BP_HE_Medium_Shell_C",
            "BP_HE_Shell_C",
        ):
            return cls.HE
        if projectile.type == "BP_Smoke_Shell_C":
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
    type: WeaponType
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

    def get_seat_type(self) -> VehicleSeatType:
        if self.name.startswith("GUNNER "):
            return VehicleSeatType.GUNNER
        if self.name == "AIMER":
            return VehicleSeatType.GUNNER

        return VehicleSeatType[to_method_name(self.name)]

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
    factions: set[AnyFaction]
    hull: VehicleCompartmentData
    turret: VehicleCompartmentData
    tracks: VehicleCompartmentData
    engine: VehicleCompartmentData
    seats: list[VehicleSeatData] = []
    exposed: bool = False

    @model_validator(mode="after")
    def set_meth_name(self) -> "VehicleData":
        metadata = game_switch(HLL_VEHICLE_METADATA, HLLV_VEHICLE_METADATA)
        meta = metadata.get(self.id)
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
        if self.type not in (
            VehicleType.ARTILLERY,
            VehicleType.ANTI_TANK_GUN,
            VehicleType.ANTI_AIRCRAFT_GUN,
            VehicleType.MORTAR,
        ):
            weapons.append(
                WeaponData(
                    meth_name=to_method_name("V_ROADKILL__" + self.id),
                    id=self.id,
                    name=self.id,
                    vehicle_id=self.id,
                    factions=self.factions,
                    type=WeaponType.ROADKILL,
                ),
            )
        for seat in self.seats:
            weapons.extend(seat.get_weapons(self, include_generic=include_generic))
        return weapons

    def to_constructor(self) -> str:
        seats: list[str] = []
        template, seat_template = game_switch(
            (HLL_VEHICLE_CONSTRUCTOR_TEMPLATE, HLL_VEHICLE_SEAT_CONSTRUCTOR_TEMPLATE),
            (HLLV_VEHICLE_CONSTRUCTOR_TEMPLATE, HLLV_VEHICLE_SEAT_CONSTRUCTOR_TEMPLATE),
        )
        for index, seat in enumerate(self.seats):
            if seat.role_types == VehicleSeatRoleTypes.TANK_CREW:
                requires_roles = game_switch(
                    "_HLL_TANK_CREW_ROLES",
                    "_HLLV_TANK_CREW_ROLES",
                )
            elif seat.role_types == VehicleSeatRoleTypes.ARTY_CREW:
                requires_roles = game_switch(
                    "_HLL_ARTY_CREW_ROLES",
                    "_HLLV_MORTAR_CREW_ROLES",
                )
            else:
                requires_roles = "None"

            weapon_cls = game_switch("HLLWeapon", "HLLVWeapon")
            weapons = stringify_list(
                [
                    f"{weapon_cls}.{weapon.meth_name}"
                    for weapon in seat.get_weapons(self)
                ],
                indent=4,
            ).lstrip()

            seats.append(
                seat_template.format(
                    index=index,
                    seat=seat,
                    type=stringify_enum_member(seat.get_seat_type()),
                    weapons=weapons,
                    requires_roles=requires_roles,
                    exposed=self.exposed,
                ),
            )

        return template.format(
            vehicle=self,
            factions=stringify_factions(self.factions, indent=3 * 4).lstrip(),
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
        factions: set[AnyFaction],
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

    def get_weapon_type(self, weapon: HLLArmorWeapon, seat_index: int) -> WeaponType:  # noqa: ARG002
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
                projectile,
            )
            if not ammo_type:
                ammo_type = VehicleWeaponAmmoType.AP
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

    def _get_weapon_ammo_mortar(
        self,
        weapon_data: VehicleWeapon,
        weapon: HLLArmorWeaponMortar,
    ) -> None:
        ammo_sources = weapon.properties.ammo_info.ammo_sources
        projectiles = weapon.get_projectiles()

        if len(projectiles) != 1:
            logger.error(
                "Unexpected number of projectiles for mortar weapon %s:"
                " Expected 1, got %s",
                weapon.properties.weapon_name,
                len(projectiles),
            )

        ammo_source = ammo_sources[0]
        projectile = projectiles[0]

        weapon_data.ammo.append(
            VehicleWeaponAmmo(
                munitions_cost=0,
                clip_size=ammo_source.clip_size,
                max_clips=ammo_source.max_clips,
                name=str(ammo_source.display_name),
                type=VehicleWeaponAmmoType.HE,
                explosion_damage=projectile.properties.explosion_damage,
                explosion_radius=projectile.properties.explosion_radius,
            ),
        )

    def _get_weapon_ammo_grenade(
        self,
        weapon_data: VehicleWeapon,
        weapon: HLLArmorWeaponGrenade,
    ) -> None:
        ammo_sources = weapon.properties.ammo_info.ammo_sources

        if len(ammo_sources) != 1:
            logger.error(
                "Unexpected number of ammo sources for grenade weapon %s:"
                " Expected 1, got %s",
                weapon.properties.weapon_name,
                len(ammo_sources),
            )

        ammo_source = ammo_sources[0]

        weapon_data.ammo.append(
            VehicleWeaponAmmo(
                munitions_cost=0,
                clip_size=ammo_source.clip_size,
                max_clips=ammo_source.max_clips,
                name=str(ammo_source.display_name),
                type=VehicleWeaponAmmoType.HE,
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
        elif isinstance(weapon, HLLArmorWeaponMortar):
            self._get_weapon_ammo_mortar(weapon_data, weapon)
        elif isinstance(weapon, HLLArmorWeaponGrenade):
            self._get_weapon_ammo_grenade(weapon_data, weapon)
        else:
            logger.warning(
                "Unexpected weapon type %s for weapon %s",
                type(weapon).__name__,
                weapon.name,
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
    def get_weapon_type(self, weapon: HLLArmorWeapon, seat_index: int) -> WeaponType:
        if isinstance(weapon, HLLArmorWeaponBallistic):
            if seat_index == 0:
                return WeaponType.TANK_HULL_MG
            return WeaponType.TANK_COAXIAL_MG

        if isinstance(weapon, HLLArmorWeaponProjectile | HLLArmorWeaponMountedHowitzer):
            return WeaponType.TANK_CANNON

        if isinstance(weapon, HLLArmorWeaponReconGun):
            return WeaponType.TANK_RECON

        if isinstance(weapon, HLLArmorWeaponSmokeScreen | HLLArmorWeaponGrenade):
            return WeaponType.TANK_SMOKE_SCREEN

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
    VehicleExtractor[
        HLLHowitzerProperties
        | HLLAntiTankGunProperties
        | HLLMortarProperties
        | HLLAntiAircraftGunProperties
    ],
):
    def get_weapon_type(self, weapon: HLLArmorWeapon, seat_index: int) -> WeaponType:
        if isinstance(weapon, HLLArmorWeaponHowitzer):
            return WeaponType.ARTILLERY
        if isinstance(weapon, HLLArmorWeaponMortar):
            return WeaponType.MORTAR
        if isinstance(weapon, HLLArmorWeaponBallistic):
            return WeaponType.MOUNTED_MG
        if isinstance(weapon, HLLArmorWeaponProjectile):
            return WeaponType.AT_GUN
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


class InfantryVehicleExtractor(
    VehicleExtractor[
        HLLTruckProperties
        | HLLHalftrackProperties
        | HLLVBoatProperties
        | HLLVHelicopterProperties
    ],
):
    def get_weapon_type(self, weapon: HLLArmorWeapon, seat_index: int) -> WeaponType:
        if isinstance(weapon, HLLArmorWeaponBallistic):
            return WeaponType.MOUNTED_MG
        if isinstance(weapon, HLLArmorWeaponProjectile):
            # TODO: Assert that this is a helicopter
            return WeaponType.RECON_FLARE

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


def get_all_ability_tables() -> Iterator[tuple[HLLMapAbilityData, set[AnyFaction]]]:
    abilities_dir, abilities_factions_map = game_switch(
        (HLL_ABILITIES_DIR, HLL_ABILITIES_FACTIONS),
        (HLLV_ABILITIES_DIR, HLLV_ABILITIES_FACTIONS),
    )
    for ability_data, ability_fp in find_objects_in_dir(
        local_to_abs_path(abilities_dir, add_ext=False),
        lambda obj: obj.type == "HLLMapAbilityData",
        obj_type=HLLMapAbilityData,
        glob_pattern="**/*_DefaultAbilities*.json",
    ):
        factions = abilities_factions_map.get(ability_fp)
        if not factions:
            if factions is None:
                logger.warning(
                    "Ability file %s not found in ABILITIES_FACTIONS mapping",
                    ability_fp,
                )
            continue
        yield ability_data, factions


def get_all_abilities() -> Iterator[tuple[HLLCommanderAbility, set[AnyFaction]]]:
    for ability_table, factions in get_all_ability_tables():
        for ability in ability_table.properties.abilities:
            if a := ability.get_ability():
                yield a, factions


def get_all_artillery() -> Iterator[tuple[HLLVehicle, VehicleType, Path]]:
    if get_root_path() == HLL_METADATA_PATH:
        for howitzer_bgc, fp in find_objects_in_dir(
            local_to_abs_path(HLL_ARTILLERY_DIR, add_ext=False),
            lambda bgc: bgc.get_root_struct_name() == "Class'HLLHowitzer'",
            obj_type=BlueprintGeneratedClass[HLLVehicle[HLLHowitzerProperties]],
            glob_pattern="**/BP_*.json",
            cond_obj_type=BlueprintGeneratedClass,
        ):
            yield (
                howitzer_bgc.get_default_object(HLLVehicle[HLLHowitzerProperties]),
                VehicleType.ARTILLERY,
                fp,
            )

        for antitank_bgc, fp in find_objects_in_dir(
            local_to_abs_path(HLL_ARTILLERY_DIR, add_ext=False),
            lambda bgc: bgc.get_root_struct_name() == "Class'HLLAntiTankGun'",
            obj_type=BlueprintGeneratedClass[HLLVehicle[HLLAntiTankGunProperties]],
            glob_pattern="**/BP_*.json",
            cond_obj_type=BlueprintGeneratedClass,
        ):
            yield (
                antitank_bgc.get_default_object(HLLVehicle[HLLAntiTankGunProperties]),
                VehicleType.ANTI_TANK_GUN,
                fp,
            )
    elif get_root_path() == HLLV_METADATA_PATH:
        for mortar_bgc, fp in find_objects_in_dir(
            local_to_abs_path(HLLV_MORTARS_DIR, add_ext=False),
            lambda bgc: bgc.get_root_struct_name() == "Class'HLLMortar'",
            obj_type=BlueprintGeneratedClass[HLLVehicle[HLLMortarProperties]],
            glob_pattern="**/BP_Mortar_*.json",
            cond_obj_type=BlueprintGeneratedClass,
        ):
            yield (
                mortar_bgc.get_default_object(HLLVehicle[HLLMortarProperties]),
                VehicleType.MORTAR,
                fp,
            )

        for antiair_bgc, fp in find_objects_in_dir(
            local_to_abs_path(HLLV_ANTI_AIR_DIR, add_ext=False),
            lambda bgc: bgc.get_root_struct_name() == "Class'HLLAntiAircraftGun'",
            obj_type=BlueprintGeneratedClass[HLLVehicle[HLLAntiAircraftGunProperties]],
            glob_pattern="**/BP_*Gun.json",
            cond_obj_type=BlueprintGeneratedClass,
        ):
            yield (
                antiair_bgc.get_default_object(
                    HLLVehicle[HLLAntiAircraftGunProperties],
                ),
                VehicleType.ANTI_AIRCRAFT_GUN,
                fp,
            )

        return
    else:
        msg = f"Unexpected root path {get_root_path()}"
        raise ValueError(msg)


UI_SUBCATEGORY_TO_VEHICLE_TYPE: dict[str, VehicleType] = {
    "HEAVY ARMOR": VehicleType.HEAVY_TANK,
    "MEDIUM ARMOR": VehicleType.MEDIUM_TANK,
    "LIGHT ARMOR": VehicleType.LIGHT_TANK,
    "RECON": VehicleType.RECON_VEHICLE,
    "SELF-PROPELLED ARTILLERY": VehicleType.SELF_PROPELLED_ARTILLERY,
    "HALF-TRACK": VehicleType.HALF_TRACK,
    "SUPPORT": VehicleType.SUPPLY_TRUCK,
}


def get_vehicle_type_from_ui_subcategory(
    vehicle_bgc: BlueprintGeneratedClass[HLLVehicle],
    ui_sub_category: str,
) -> VehicleType:
    vehicle_type = UI_SUBCATEGORY_TO_VEHICLE_TYPE[ui_sub_category]
    if vehicle_type != VehicleType.SUPPLY_TRUCK:
        return vehicle_type

    vehicle_struct = vehicle_bgc.get_root_struct_name()
    if vehicle_struct == "Class'BaseJeep'":
        return VehicleType.JEEP
    if vehicle_struct == "Class'BaseTruck'":
        if "transport" in vehicle_bgc.name.lower():
            return VehicleType.TRANSPORT_TRUCK
        if "supply" in vehicle_bgc.name.lower():
            return VehicleType.SUPPLY_TRUCK
        msg = (
            "Cannot determine vehicle type for BaseTruck with name"
            f" '{vehicle_bgc.name}'"
        )
        raise ValueError(msg)
    if vehicle_struct == "Class'BaseWaterfallBoat'":
        return VehicleType.BOAT
    if vehicle_struct == "Class'BaseHelicopter'":
        return VehicleType.HELICOPTER
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
    "Class'WFLBaseTank'": HLLVehicle[HLLArmorProperties],
    "Class'BaseWaterfallBoat'": HLLVehicle[HLLVBoatProperties],
    "Class'BaseHelicopter'": HLLVehicle[HLLVHelicopterProperties],
}


def get_vehicle_class_from_root_struct(
    vehicle_bgc: BlueprintGeneratedClass[HLLVehicle],
) -> type[HLLVehicle]:
    struct_name = vehicle_bgc.get_root_struct_name()
    if struct_name not in STRUCT_NAME_TO_VEHICLE_CLASS:
        msg = f"Unexpected vehicle struct '{struct_name}' for vehicle {vehicle_bgc}"
        raise ValueError(msg)
    return STRUCT_NAME_TO_VEHICLE_CLASS[struct_name]


def _get_all_vehicle_attributes() -> Iterator[
    tuple[HLLVehicle, VehicleType, set[AnyFaction]]
]:
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

    for vehicle, vehicle_type, vehicle_fp in get_all_artillery():
        artillery_factions = game_switch(
            HLL_ARTILLERY_FACTIONS,
            HLLV_ARTILLERY_FACTIONS,
        )
        if vehicle_fp not in artillery_factions:
            logger.warning(
                "Artillery file %s not found in ARTILLERY_FACTIONS mapping",
                vehicle_fp,
            )
            continue

        if not artillery_factions[vehicle_fp]:
            continue

        factions = artillery_factions[vehicle_fp]
        yield vehicle, vehicle_type, factions


def get_all_vehicle_attributes() -> Iterator[
    tuple[HLLVehicle, VehicleType, set[AnyFaction]]
]:
    seen: dict[HLLVehicle, tuple[VehicleType, set[AnyFaction]]] = {}

    for vehicle, vehicle_type, factions in _get_all_vehicle_attributes():
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
    for vehicle, vehicle_type, factions in get_all_vehicle_attributes():
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
            (
                HLLHowitzerProperties,
                HLLAntiTankGunProperties,
                HLLMortarProperties,
                HLLAntiAircraftGunProperties,
            ),
        ):
            data = ArtilleryVehicleExtractor(
                cast(
                    "HLLVehicle[HLLHowitzerProperties | HLLAntiTankGunProperties]",
                    vehicle,
                ),
                vehicle_type,
                factions,
            ).extract()
        elif isinstance(
            vehicle.properties,
            (HLLVBoatProperties, HLLVHelicopterProperties),
        ):
            data = InfantryVehicleExtractor(
                cast(
                    "HLLVehicle[HLLVBoatProperties | HLLVHelicopterProperties]",
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


def get_all_vehicles() -> Iterator[VehicleData]:
    vehicle_data = sorted(get_all_vehicle_data(), key=lambda v: v.id)
    vehicle_ids = itertools.groupby(vehicle_data, lambda v: v.id)
    for _, vd_seq in vehicle_ids:
        yield VehicleData.merge(*vd_seq)


def get_all_vehicle_weapons(vehicles: list[VehicleData]) -> Iterator[WeaponData]:
    weapon_data = sorted(
        (
            weapon
            for vehicle in vehicles
            for weapon in vehicle.get_weapons(include_generic=True)
        ),
        key=lambda w: w.id,
    )
    weapon_ids = itertools.groupby(weapon_data, lambda w: w.id)
    for _, wd_seq in weapon_ids:
        yield WeaponData.merge(*wd_seq)


def main() -> None:

    with root_path_ctx(HLL_METADATA_PATH):
        vehicles = list(get_all_vehicles())
        vehicle_constructors = [v.to_constructor() for v in vehicles]

        inject_code(
            Path("hllrcon/data/vehicles.py"),
            "hll vehicles",
            "\n\n".join(vehicle_constructors),
        )

        Path("dist").mkdir(exist_ok=True)
        Path("dist/vehicles.json").write_bytes(
            TypeAdapter(list[VehicleData]).dump_json(vehicles, indent=2),
        )

        weapons = list(get_all_vehicle_weapons(vehicles))
        weapon_constructors = [w.to_constructor() for w in weapons]

        inject_code(
            Path("hllrcon/data/weapons.py"),
            "hll vehicles",
            "\n\n".join(weapon_constructors),
        )

    with root_path_ctx(HLLV_METADATA_PATH):
        vehicles = list(get_all_vehicles())
        vehicle_constructors = [v.to_constructor() for v in vehicles]

        inject_code(
            Path("hllrcon/data/vehicles.py"),
            "hllv vehicles",
            "\n\n".join(vehicle_constructors),
        )

        Path("dist").mkdir(exist_ok=True)
        Path("dist/vehicles_vietnam.json").write_bytes(
            TypeAdapter(list[VehicleData]).dump_json(vehicles, indent=2),
        )

        weapons = list(get_all_vehicle_weapons(vehicles))
        weapon_constructors = [w.to_constructor() for w in weapons]

        inject_code(
            Path("hllrcon/data/weapons.py"),
            "hllv vehicles",
            "\n\n".join(weapon_constructors),
        )


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
    "Jeep": {
        "name": "Willy's Jeep",
        "exposed": True,
    },
    "60L (Supply)": {
        "meth_name": "FORD_F60L_SUPPLY",
        "name": "Ford F60L",
        "exposed": True,
    },
    "60L (Transport)": {
        "meth_name": "FORD_F60L_TRANSPORT",
        "name": "Ford F60L",
        "exposed": True,
    },
    "Half-track": {
        "name": "M3 Half-track",
        "exposed": True,
    },
}

HLLV_VEHICLE_METADATA: dict[str, VehicleMetaData] = {
    "Gaz 63 (Transport)": {
        "name": "GAZ-63",
        "exposed": True,
    },
    "Gaz 63 (Supply)": {
        "name": "GAZ-63",
        "exposed": True,
    },
    "Sd.Kfz.171 T54": {
        "name": "T-54",
        "exposed": False,
    },
    "Sd.Kfz.171 M48Patton": {
        "name": "M48 Patton",
        "exposed": False,
    },
    "NVA Boat": {
        "name": "NVA Boat",
        "exposed": True,
    },
    "US Transport Helicopter": {
        "name": "Bell UH-1 Iroquois",
        "exposed": True,
    },
    "US Supply Helicopter": {
        "name": "Bell UH-1 Iroquois",
        "exposed": True,
    },
    "M35 (Transport)": {
        "name": "M35 Truck",
        "exposed": True,
    },
    "M35 (Supply)": {
        "name": "M35 Truck",
        "exposed": True,
    },
    "US Boat": {
        "name": "PBR",
        "exposed": True,
    },
    "MORTAR": {
        "name": "Mortar",
        "exposed": True,
    },
    "DShKM Anti-Aircraft Gun": {
        "name": "DShKM",
        "exposed": True,
    },
}

if __name__ == "__main__":
    main()
