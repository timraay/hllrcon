# ruff: noqa: N802

from typing import TYPE_CHECKING, ClassVar

from ._utils import IndexedBaseModel, class_cached_property
from .teams import Team


class Faction(IndexedBaseModel[int, None]):
    UNASSIGNED_ID: ClassVar[int] = 6

    name: str
    short_name: str
    team: Team

    @classmethod
    def _lookup_fallback(cls, id_: int) -> "Faction | None":
        if id_ == cls.UNASSIGNED_ID:
            return None

        return super()._lookup_fallback(id_)

    if TYPE_CHECKING:

        @classmethod
        def by_id(cls, id_: int) -> "Faction | None":
            """Look up a faction by its identifier.

            Parameters
            ----------
            id_ : int
                The identifier of the faction to look up.

            Returns
            -------
            Faction | None
                The faction instance with the given identifier, or `None` if the
                identifier corresponds with being unassigned.

            Raises
            ------
            ValueError
                If no faction with the given identifier exists.

            """

    @class_cached_property
    @classmethod
    def GER(cls) -> "Faction":
        return cls(id=0, name="Germany", short_name="GER", team=Team.AXIS)

    @class_cached_property
    @classmethod
    def US(cls) -> "Faction":
        return cls(id=1, name="United States", short_name="US", team=Team.ALLIES)

    @class_cached_property
    @classmethod
    def SOV(cls) -> "Faction":
        return cls(id=2, name="Soviet Union", short_name="SOV", team=Team.AXIS)

    @class_cached_property
    @classmethod
    def RUS(cls) -> "Faction":
        return cls.SOV

    @class_cached_property
    @classmethod
    def CW(cls) -> "Faction":
        return cls(id=3, name="Allies", short_name="CW", team=Team.ALLIES)

    @class_cached_property
    @classmethod
    def GB(cls) -> "Faction":
        return cls.CW

    @class_cached_property
    @classmethod
    def DAK(cls) -> "Faction":
        return cls(
            id=4,
            name="German Africa Corps",
            short_name="DAK",
            team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def B8A(cls) -> "Faction":
        return cls(
            id=5,
            name="British Eighth Army",
            short_name="B8A",
            team=Team.ALLIES,
        )
