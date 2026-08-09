from enum import StrEnum

from hllrcon.data.maps import CardinalDirection


class EMapOrientation(StrEnum):
    LEFT_TO_RIGHT = "EMapOrientation::LeftToRight"
    RIGHT_TO_LEFT = "EMapOrientation::RightToLeft"
    TOP_TO_BOTTOM = "EMapOrientation::TopToBottom"
    BOTTOM_TO_TOP = "EMapOrientation::BottomToTop"

    def to_cardinal_direction(self) -> CardinalDirection:
        return CardinalDirection[self.name]
