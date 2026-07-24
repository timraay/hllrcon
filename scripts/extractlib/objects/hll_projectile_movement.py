from typing import Annotated

from pydantic import Field

from scripts.extractlib.loader import Model, Object


class HLLProjectileMovementProperties(Model):
    initial_speed: float
    max_speed: float
    projectile_gravity_scale: float
    should_bounce: Annotated[bool, Field(alias="ShouldBounce")] = False
    """Whether the projectile can bounce off of armor."""
    bounciness: float = 0.0
    friction: float = 0.0


class HLLProjectileMovement(Object[HLLProjectileMovementProperties]):
    pass
