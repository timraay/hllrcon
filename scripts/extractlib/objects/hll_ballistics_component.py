from scripts.extractlib.loader import Model, Object, ObjectReference
from scripts.extractlib.objects.hll_projectile_bullet import HLLProjectileBullet


class HLLBallisticsComponentProperties(Model):
    projectile_class: ObjectReference[HLLProjectileBullet]


class HLLBallisticsComponent(Object[HLLBallisticsComponentProperties]):
    pass
