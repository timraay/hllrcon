from scripts.extractlib.loader import Model, Object, ObjectReference
from scripts.extractlib.objects.sphere_component import SphereComponent


class SphereSectorCaptureBoosterProperties(Model):
    trigger_shape: ObjectReference[SphereComponent]
    map_component: ObjectReference
    root_component: ObjectReference


class SphereSectorCaptureBooster(Object[SphereSectorCaptureBoosterProperties]):
    pass
