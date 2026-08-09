from functools import total_ordering
from typing import Any

from scripts.extractlib.loader import Model


@total_ordering
class Vec2(Model):
    x: float
    y: float

    def __bool__(self) -> bool:
        return bool(self.x or self.y)

    def __lt__(self, other: Any) -> bool:  # noqa: ANN401
        if isinstance(other, Vec2):
            return (self.x, self.y) < (other.x, other.y)
        return NotImplemented
