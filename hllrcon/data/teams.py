# ruff: noqa: N802


from typing import TypeAlias

from ._utils import IndexedBaseModel, class_cached_property


class _Team(IndexedBaseModel[int]):
    id: int
    name: str


class HLLTeam(_Team):
    @class_cached_property
    @classmethod
    def ALLIES(cls) -> "HLLTeam":
        return cls(id=1, name="Allies")

    @class_cached_property
    @classmethod
    def AXIS(cls) -> "HLLTeam":
        return cls(id=2, name="Axis")


class HLLVTeam(_Team):
    @class_cached_property
    @classmethod
    def SOUTH(cls) -> "HLLVTeam":
        return cls(id=1, name="South")

    @class_cached_property
    @classmethod
    def ALLIES(cls) -> "HLLVTeam":
        return cls.SOUTH

    @class_cached_property
    @classmethod
    def NORTH(cls) -> "HLLVTeam":
        return cls(id=2, name="North")

    @class_cached_property
    @classmethod
    def AXIS(cls) -> "HLLVTeam":
        return cls.NORTH


Team: TypeAlias = HLLTeam | HLLVTeam
