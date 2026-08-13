from typing import Any

from scripts.extractlib.loader import Model, Object, ObjectReference
from scripts.extractlib.objects.level import Level


class World(Object[Model]):
    persistent_level: ObjectReference[Level]
    extra_referenced_objects: list[ObjectReference[Any]]
    streaming_levels: list[ObjectReference[Any]]
