from typing import Any

from scripts.extractlib.structs.vec2 import Vec2


class Vec3(Vec2):
    z: float

    def __bool__(self) -> bool:
        return bool(self.x or self.y or self.z)

    def __lt__(self, other: Any) -> bool:  # noqa: ANN401
        if isinstance(other, Vec3):
            return (self.x, self.y, self.z) < (other.x, other.y, other.z)
        return NotImplemented
