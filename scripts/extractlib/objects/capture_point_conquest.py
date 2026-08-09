from typing import Any

from scripts.extractlib.loader import Model, Object, ObjectReference
from scripts.extractlib.objects.sphere_component import SphereComponent
from scripts.extractlib.types import String


class CapturePointConquestProperties(Model):
    objective_name: String
    objective_call_sign: String
    soft_capture_point_shape: ObjectReference[Any]
    hard_capture_point_shape: ObjectReference[SphereComponent]
    linked_sectors_territories: list[int]

    def get_hard_capture_point_shape(self) -> SphereComponent:
        return self.hard_capture_point_shape.get(SphereComponent)


class CapturePointConquest(Object[CapturePointConquestProperties]):
    pass
