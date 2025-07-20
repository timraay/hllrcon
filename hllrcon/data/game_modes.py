from enum import StrEnum

from hllrcon.data.utils import IndexedBaseModel


class GameModeScale(StrEnum):
    LARGE = "large"
    SMALL = "small"


class GameMode(IndexedBaseModel[str]):
    id: str
    scale: GameModeScale

    def is_large(self) -> bool:
        return self.scale == GameModeScale.LARGE

    def is_small(self) -> bool:
        return self.scale == GameModeScale.SMALL


WARFARE = GameMode(id="warfare", scale=GameModeScale.LARGE)
OFFENSIVE = GameMode(id="offensive", scale=GameModeScale.LARGE)
SKIRMISH = GameMode(id="skirmish", scale=GameModeScale.SMALL)


def by_id(game_mode_id: str) -> GameMode:
    return GameMode.by_id(game_mode_id)
