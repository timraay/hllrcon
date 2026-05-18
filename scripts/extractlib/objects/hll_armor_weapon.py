from enum import StrEnum
from typing import Annotated

from pydantic import Field

from scripts.extractlib.loader import Model, Object
from scripts.extractlib.objects.blueprint_generated_class import BGCReference
from scripts.extractlib.objects.hll_ballistics_component import HLLBallisticsComponent
from scripts.extractlib.objects.hll_howitzer_projectile import HLLHowitzerProjectile
from scripts.extractlib.objects.hll_projectile_bullet import HLLProjectileBullet
from scripts.extractlib.objects.shooter_projectile import ShooterProjectile
from scripts.extractlib.structs.vec2 import Vec2
from scripts.extractlib.types import CultureInvariantString, String


class EShellType(StrEnum):
    AP = "EAmmoShellType::AST_AP"
    HE = "EAmmoShellType::AST_HE"
    SMOKE = "EAmmoShellType::AST_SMOKE"  # Artillery Smoke
    MAX = "EAmmoShellType::AST_MAX"  # Tank Smoke
    NONE = "EAmmoShellType::AST_NONE"  # SPA, Recon Gun, Half-Track


class EAmmoSourceType(StrEnum):
    LOCAL = "EAmmoSourceType::AST_Local"
    MUNITIONS = "EAmmoSourceType::AST_Munitions"
    ARTILLERY = "EAmmoSourceType::AST_Artillery"


class HLLArmorWeaponAmmoSource(Model):
    ammo_type: EAmmoSourceType = EAmmoSourceType.LOCAL
    ammo_cost: int = 0
    clip_size: int = 200
    max_clips: int = 6
    display_name: Annotated[
        String,
        Field(
            default_factory=lambda: CultureInvariantString(
                culture_invariant_string=None,
            ),
        ),
    ]
    is_shell: Annotated[bool, Field(alias="bIsShell")] = False
    shell_type: EShellType = EShellType.NONE


class HLLArmorWeaponAmmoInfo(Model):
    init_loaded: Annotated[bool, Field(alias="bInitLoaded")] = False
    ammo_sources: Annotated[
        list[HLLArmorWeaponAmmoSource],
        Field(default_factory=lambda: [HLLArmorWeaponAmmoSource()]),
    ]


class HLLArmorWeaponProperties(Model):
    ammo_info: Annotated[
        HLLArmorWeaponAmmoInfo,
        Field(default_factory=HLLArmorWeaponAmmoInfo),
    ]
    cancel_reload_on_occupancy_change: Annotated[
        bool,
        Field(alias="bCancelReloadOnOccupancyChange"),
    ] = False
    disable_loading_when_weapon_damaged: Annotated[
        bool,
        Field(alias="bDisableLoadingWhenWeaponDamaged"),
    ] = False
    disable_loading_health_ratio: float = 0.0
    min_load_time: float
    weapon_name: String | None = None
    weapon_header: String | None = None
    disable_firing_when_weapon_damaged: Annotated[
        bool,
        Field(alias="bDisableFiringWhenWeaponDamaged"),
    ] = False
    disable_firing_health_ratio: float = 0.0
    shot_delay: float = 1.0
    auto_reload_when_empty: Annotated[
        bool,
        Field(alias="bAutoReloadWhenEmpty"),
    ] = False
    recoil_impulse_magnitude: float = 0.0
    camera_shake_radius: float = 0.0


class HLLArmorWeaponBallisticProperties(HLLArmorWeaponProperties):
    ballistic_handler: BGCReference[HLLBallisticsComponent]


class HLLArmorWeaponProjectileProperties(HLLArmorWeaponProperties):
    projectiles: list[BGCReference[ShooterProjectile]]


class HLLArmorWeaponReconGunProperties(HLLArmorWeaponProperties):
    pass


class HLLArmorWeaponHowitzerProperties(HLLArmorWeaponProperties):
    min_max_dispersion: Vec2
    min_max_dispersion_within_outpost_range: Vec2
    projectiles: Annotated[
        list[BGCReference[HLLHowitzerProjectile]],
        Field(alias="Shells"),
    ]
    observer_outpost_range: float = 0.0


class HLLArmorWeaponMountedHowitzerProperties(HLLArmorWeaponProperties):
    min_max_range: Vec2
    inverted_artillery_mode_min_max_pitch: Vec2
    max_stationary_speed: float
    max_stationary_velocity: float
    min_max_dispersion: Vec2
    min_max_dispersion_within_outpost_range: Vec2
    projectiles: Annotated[
        list[BGCReference[ShooterProjectile]],
        Field(alias="PhysicalShells"),
    ]
    observer_outpost_range: float


class HLLArmorWeaponSmokeScreenProperties(HLLArmorWeaponProperties):
    pass


class HLLArmorWeaponBallistic(Object[HLLArmorWeaponBallisticProperties]):
    shot_delay: float = 0.1

    def get_projectile(self) -> HLLProjectileBullet:
        ballistics = self.properties.ballistic_handler.get_inst(HLLBallisticsComponent)
        return ballistics.properties.projectile_class.get(HLLProjectileBullet)


class HLLArmorWeaponProjectile(Object[HLLArmorWeaponProjectileProperties]):
    def get_projectiles(self) -> list[ShooterProjectile]:
        return [
            projectile.get_inst(ShooterProjectile)
            for projectile in self.properties.projectiles
        ]


class HLLArmorWeaponReconGun(Object[HLLArmorWeaponReconGunProperties]):
    pass


class HLLArmorWeaponHowitzer(Object[HLLArmorWeaponHowitzerProperties]):
    def get_projectiles(self) -> list[HLLHowitzerProjectile]:
        return [
            projectile.get_inst(HLLHowitzerProjectile)
            for projectile in self.properties.projectiles
        ]


class HLLArmorWeaponMountedHowitzer(Object[HLLArmorWeaponMountedHowitzerProperties]):
    def get_projectiles(self) -> list[ShooterProjectile]:
        return [
            projectile.get_inst(ShooterProjectile)
            for projectile in self.properties.projectiles
        ]


class HLLArmorWeaponSmokeScreen(Object[HLLArmorWeaponSmokeScreenProperties]):
    pass


HLLArmorWeapon = (
    HLLArmorWeaponBallistic
    | HLLArmorWeaponProjectile
    | HLLArmorWeaponReconGun
    | HLLArmorWeaponHowitzer
    | HLLArmorWeaponMountedHowitzer
    | HLLArmorWeaponSmokeScreen
)
