from scripts.extractlib.loader import Model, Object
from scripts.extractlib.objects.blueprint_generated_class import BGCReference
from scripts.extractlib.objects.shooter_damage_type import ShooterDamageType
from scripts.extractlib.structs.team import ETeam


class HLLHowitzerProjectileProperties(Model):
    incoming_delay: float
    explode_delay: float
    damage: float = 0.0
    damage_radius: float = 0.0
    damage_type: BGCReference[ShooterDamageType] | None = None
    suppression: float = 0.0
    suppression_radius: float = 0.0
    shell_team: ETeam


class HLLHowitzerProjectile(Object[HLLHowitzerProjectileProperties]):
    pass
