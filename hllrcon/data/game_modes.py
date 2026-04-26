# ruff: noqa: N802

from enum import StrEnum
from typing import Never, TypeAlias

from ._utils import (
    CaseInsensitiveIndexedBaseModel,
    class_cached_property,
)


class GameModeScale(StrEnum):
    LARGE = "large"
    SMALL = "small"


class _GameMode(CaseInsensitiveIndexedBaseModel[Never]):
    scale: GameModeScale

    def is_large(self) -> bool:
        return self.scale == GameModeScale.LARGE

    def is_small(self) -> bool:
        return self.scale == GameModeScale.SMALL


class HLLGameMode(_GameMode):
    @class_cached_property
    @classmethod
    def WARFARE(cls) -> "HLLGameMode":
        return cls(id="warfare", scale=GameModeScale.LARGE)

    @class_cached_property
    @classmethod
    def OFFENSIVE(cls) -> "HLLGameMode":
        return cls(id="offensive", scale=GameModeScale.LARGE)

    @class_cached_property
    @classmethod
    def CONQUEST(cls) -> "HLLGameMode":
        return cls(id="conquest", scale=GameModeScale.LARGE)

    @class_cached_property
    @classmethod
    def SKIRMISH(cls) -> "HLLGameMode":
        return cls(id="skirmish", scale=GameModeScale.SMALL)


class HLLVGameMode(_GameMode):
    @class_cached_property
    @classmethod
    def WARFARE(cls) -> "HLLVGameMode":
        return cls(id="warfare", scale=GameModeScale.LARGE)

    @class_cached_property
    @classmethod
    def OFFENSIVE(cls) -> "HLLVGameMode":
        return cls(id="offensive", scale=GameModeScale.LARGE)

    @class_cached_property
    @classmethod
    def CONQUEST(cls) -> "HLLVGameMode":
        return cls(id="conquest", scale=GameModeScale.LARGE)

    @class_cached_property
    @classmethod
    def DOMINATION(cls) -> "HLLVGameMode":
        return cls(id="domination", scale=GameModeScale.LARGE)

    @class_cached_property
    @classmethod
    def SKIRMISH(cls) -> "HLLVGameMode":
        return cls(id="skirmish", scale=GameModeScale.SMALL)


GameMode: TypeAlias = HLLGameMode | HLLVGameMode
