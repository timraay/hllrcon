# ruff: noqa: N802

from typing import TYPE_CHECKING, Annotated, ClassVar, Generic, Self, TypeAlias, TypeVar

from ._utils import IndexedBaseModel, class_cached_property, model_serializer
from .teams import HLLTeam, HLLVTeam, _Team

TeamT = TypeVar("TeamT", bound=_Team)


class _Faction(IndexedBaseModel[int, None], Generic[TeamT]):
    UNASSIGNED_ID: ClassVar[int] = -1

    id: int
    name: str
    short_name: str
    team: Annotated[
        TeamT,
        model_serializer(int),
    ]

    @classmethod
    def _lookup_fallback(cls, id_: int) -> "Self | None":
        if id_ == cls.UNASSIGNED_ID:
            return None

        return super()._lookup_fallback(id_)

    if TYPE_CHECKING:

        @classmethod
        def by_id(cls, id_: int) -> "Self | None":
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


class HLLFaction(_Faction[HLLTeam]):
    UNASSIGNED_ID: ClassVar[int] = 6

    @property
    def is_allied(self) -> bool:
        """Whether the faction is part of the allied forces.

        Allied factions are:
        - United States (`US`)
        - Soviet Union (`SOV`)
        - Commonwealth (`CW`)
        - British 8th Army (`B8A`)
        """
        return self.team == HLLTeam.ALLIES

    @property
    def is_axis(self) -> bool:
        """Whether the faction is part of the axis forces.

        Axis factions are:
        - Germany (`GER`)
        - German Africa Corps (`DAK`)
        """
        return self.team == HLLTeam.AXIS

    @class_cached_property
    @classmethod
    def GER(cls) -> "HLLFaction":
        return cls(
            id=0,
            name="Germany",
            short_name="GER",
            team=HLLTeam.AXIS,
        )

    @class_cached_property
    @classmethod
    def US(cls) -> "HLLFaction":
        return cls(
            id=1,
            name="United States",
            short_name="US",
            team=HLLTeam.ALLIES,
        )

    @class_cached_property
    @classmethod
    def SOV(cls) -> "HLLFaction":
        return cls(
            id=2,
            name="Soviet Union",
            short_name="SOV",
            team=HLLTeam.ALLIES,
        )

    @class_cached_property
    @classmethod
    def RUS(cls) -> "HLLFaction":
        return cls.SOV

    @class_cached_property
    @classmethod
    def CW(cls) -> "HLLFaction":
        return cls(
            id=3,
            name="Allies",
            short_name="CW",
            team=HLLTeam.ALLIES,
        )

    @class_cached_property
    @classmethod
    def GB(cls) -> "HLLFaction":
        return cls.CW

    @class_cached_property
    @classmethod
    def DAK(cls) -> "HLLFaction":
        return cls(
            id=4,
            name="German Africa Corps",
            short_name="DAK",
            team=HLLTeam.AXIS,
        )

    @class_cached_property
    @classmethod
    def B8A(cls) -> "HLLFaction":
        return cls(
            id=5,
            name="British Eighth Army",
            short_name="B8A",
            team=HLLTeam.ALLIES,
        )


class HLLVFaction(_Faction[HLLVTeam]):
    UNASSIGNED_ID: ClassVar[int] = 8

    @property
    def is_southern(self) -> bool:
        """Whether the faction is part of the southern ("allied") forces.

        Southern factions are:
        - United States (`US`)
        """
        return self.team == HLLVTeam.SOUTH

    @property
    def is_northern(self) -> bool:
        """Whether the faction is part of the northern ("axis") forces.

        Northern factions are:
        - North-Vietnamese Army (`NVA`)
        """
        return self.team == HLLVTeam.NORTH

    is_allied = is_southern
    is_axis = is_northern

    @class_cached_property
    @classmethod
    def US(cls) -> "HLLVFaction":
        return cls(
            id=1,
            name="United States",
            short_name="US",
            team=HLLVTeam.SOUTH,
        )

    @class_cached_property
    @classmethod
    def NVA(cls) -> "HLLVFaction":
        return cls(
            id=6,
            name="NVA",
            short_name="NVA",
            team=HLLVTeam.NORTH,
        )


Faction: TypeAlias = HLLFaction | HLLVFaction
