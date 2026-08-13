from enum import StrEnum
from typing import assert_never

from hllrcon.data.teams import HLLVTeam


class ETeam(StrEnum):
    NONE = "ETeam::None"
    ALLIES = "ETeam::Allies"
    AXIS = "ETeam::Axis"

    def to_hllv_team(self) -> HLLVTeam | None:
        match self:
            case ETeam.NONE:
                return None
            case ETeam.ALLIES:
                return HLLVTeam.ALLIES
            case ETeam.AXIS:
                return HLLVTeam.AXIS
            case _:
                assert_never(self)
