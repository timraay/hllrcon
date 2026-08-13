from typing import Any

from scripts.extractlib.loader import Model, Object, ObjectReference


class LevelProperties(Model):
    model: ObjectReference[Any]
    level_build_data_id: str
    world_settings: ObjectReference[Any]


class Level(Object[LevelProperties]):
    actors: list[ObjectReference[Any] | None]
