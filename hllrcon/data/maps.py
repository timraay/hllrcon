# mypy: disable-error-code="prop-decorator"
# ruff: noqa: N802
from enum import StrEnum
from functools import cached_property
from typing import Annotated, Generic, TypeAlias, TypeVar

from pydantic import computed_field

from ._utils import (
    CaseInsensitiveIndexedBaseModel,
    R,
    class_cached_property,
    model_serializer,
)
from .factions import HLLFaction, HLLVFaction, _Faction

FactionT = TypeVar("FactionT", bound=_Faction)


class CardinalDirection(StrEnum):
    LEFT_TO_RIGHT = "left to right"
    RIGHT_TO_LEFT = "right to left"
    TOP_TO_BOTTOM = "top to bottom"
    BOTTOM_TO_TOP = "bottom to top"


class Orientation(StrEnum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class _Map(CaseInsensitiveIndexedBaseModel[R], Generic[FactionT, R]):
    name: str
    tag: str
    year: int
    pretty_name: str
    short_name: str
    allies: Annotated[
        FactionT,
        model_serializer(int),
    ]
    axis: Annotated[
        FactionT,
        model_serializer(int),
    ]

    allies_direction: CardinalDirection
    """The direction from which the Allied team has to attack."""

    @computed_field
    @cached_property
    def axis_direction(self) -> CardinalDirection:
        """The direction from which the Axis team has to attack."""
        match self.allies_direction:
            case CardinalDirection.LEFT_TO_RIGHT:
                return CardinalDirection.RIGHT_TO_LEFT
            case CardinalDirection.RIGHT_TO_LEFT:
                return CardinalDirection.LEFT_TO_RIGHT
            case CardinalDirection.TOP_TO_BOTTOM:
                return CardinalDirection.BOTTOM_TO_TOP
            case CardinalDirection.BOTTOM_TO_TOP:
                return CardinalDirection.TOP_TO_BOTTOM
            case _:  # pragma: no cover
                msg = f"Invalid direction: {self.allies_direction}"
                raise ValueError(msg)

    @computed_field
    @cached_property
    def orientation(self) -> Orientation:
        """Whether teams start horizontally or vertically from one another."""
        match self.allies_direction:
            case CardinalDirection.LEFT_TO_RIGHT | CardinalDirection.RIGHT_TO_LEFT:
                return Orientation.HORIZONTAL
            case CardinalDirection.TOP_TO_BOTTOM | CardinalDirection.BOTTOM_TO_TOP:
                return Orientation.VERTICAL
            case _:  # pragma: no cover
                msg = f"Invalid direction: {self.allies_direction}"
                raise ValueError(msg)

    @computed_field
    @cached_property
    def is_mirrored(self) -> bool:
        """If the side each faction starts at is mirrored or not.

        By default, Allies spawn left/top, Axis spawn right/bottom.
        """
        return self.allies_direction in (
            CardinalDirection.RIGHT_TO_LEFT,
            CardinalDirection.BOTTOM_TO_TOP,
        )

    def __str__(self) -> str:
        return self.id


class HLLMap(_Map[HLLFaction]):
    @class_cached_property
    @classmethod
    def CARENTAN(cls) -> "HLLMap":
        return cls(
            id="carentan",
            name="CARENTAN",
            tag="CAR",
            year=1944,
            pretty_name="Carentan",
            short_name="Carentan",
            allies=HLLFaction.US,
            axis=HLLFaction.GER,
            allies_direction=CardinalDirection.LEFT_TO_RIGHT,
        )

    @class_cached_property
    @classmethod
    def DRIEL(cls) -> "HLLMap":
        return cls(
            id="driel",
            name="DRIEL",
            tag="DRL",
            year=1944,
            pretty_name="Driel",
            short_name="Driel",
            allies=HLLFaction.CW,
            axis=HLLFaction.GER,
            allies_direction=CardinalDirection.BOTTOM_TO_TOP,
        )

    @class_cached_property
    @classmethod
    def EL_ALAMEIN(cls) -> "HLLMap":
        return cls(
            id="elalamein",
            name="EL ALAMEIN",
            tag="ELA",
            year=1942,
            pretty_name="El Alamein",
            short_name="Alamein",
            allies=HLLFaction.B8A,
            axis=HLLFaction.DAK,
            allies_direction=CardinalDirection.RIGHT_TO_LEFT,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_RIDGE(cls) -> "HLLMap":
        return cls(
            id="elsenbornridge",
            name="ELSENBORN RIDGE",
            tag="EBR",
            year=1944,
            pretty_name="Elsenborn Ridge",
            short_name="Elsenborn",
            allies=HLLFaction.US,
            axis=HLLFaction.GER,
            allies_direction=CardinalDirection.BOTTOM_TO_TOP,
        )

    @class_cached_property
    @classmethod
    def FOY(cls) -> "HLLMap":
        return cls(
            id="foy",
            name="FOY",
            tag="FOY",
            year=1944,
            pretty_name="Foy",
            short_name="Foy",
            allies=HLLFaction.US,
            axis=HLLFaction.GER,
            allies_direction=CardinalDirection.BOTTOM_TO_TOP,
        )

    @class_cached_property
    @classmethod
    def HILL_400(cls) -> "HLLMap":
        return cls(
            id="hill400",
            name="HILL 400",
            tag="HIL",
            year=1944,
            pretty_name="Hill 400",
            short_name="Hill 400",
            allies=HLLFaction.US,
            axis=HLLFaction.GER,
            allies_direction=CardinalDirection.LEFT_TO_RIGHT,
        )

    @class_cached_property
    @classmethod
    def HURTGEN_FOREST(cls) -> "HLLMap":
        return cls(
            id="hurtgenforest",
            name="HÜRTGEN FOREST",
            tag="HUR",
            year=1944,
            pretty_name="Hurtgen Forest",
            short_name="Hurtgen",
            allies=HLLFaction.US,
            axis=HLLFaction.GER,
            allies_direction=CardinalDirection.LEFT_TO_RIGHT,
        )

    @class_cached_property
    @classmethod
    def KHARKOV(cls) -> "HLLMap":
        return cls(
            id="kharkov",
            name="Kharkov",
            tag="KHA",
            year=1943,
            pretty_name="Kharkov",
            short_name="Kharkov",
            allies=HLLFaction.SOV,
            axis=HLLFaction.GER,
            allies_direction=CardinalDirection.BOTTOM_TO_TOP,
        )

    @class_cached_property
    @classmethod
    def KURSK(cls) -> "HLLMap":
        return cls(
            id="kursk",
            name="KURSK",
            tag="KUR",
            year=1943,
            pretty_name="Kursk",
            short_name="Kursk",
            allies=HLLFaction.SOV,
            axis=HLLFaction.GER,
            allies_direction=CardinalDirection.BOTTOM_TO_TOP,
        )

    @class_cached_property
    @classmethod
    def MORTAIN(cls) -> "HLLMap":
        return cls(
            id="mortain",
            name="MORTAIN",
            tag="MOR",
            year=1944,
            pretty_name="Mortain",
            short_name="Mortain",
            allies=HLLFaction.US,
            axis=HLLFaction.GER,
            allies_direction=CardinalDirection.LEFT_TO_RIGHT,
        )

    @class_cached_property
    @classmethod
    def OMAHA_BEACH(cls) -> "HLLMap":
        return cls(
            id="omahabeach",
            name="OMAHA BEACH",
            tag="OMA",
            year=1944,
            pretty_name="Omaha Beach",
            short_name="Omaha",
            allies=HLLFaction.US,
            axis=HLLFaction.GER,
            allies_direction=CardinalDirection.RIGHT_TO_LEFT,
        )

    @class_cached_property
    @classmethod
    def PURPLE_HEART_LANE(cls) -> "HLLMap":
        return cls(
            id="purpleheartlane",
            name="PURPLE HEART LANE",
            tag="PHL",
            year=1944,
            pretty_name="Purple Heart Lane",
            short_name="PHL",
            allies=HLLFaction.US,
            axis=HLLFaction.GER,
            allies_direction=CardinalDirection.BOTTOM_TO_TOP,
        )

    @class_cached_property
    @classmethod
    def REMAGEN(cls) -> "HLLMap":
        return cls(
            id="remagen",
            name="REMAGEN",
            tag="REM",
            year=1945,
            pretty_name="Remagen",
            short_name="Remagen",
            allies=HLLFaction.US,
            axis=HLLFaction.GER,
            allies_direction=CardinalDirection.BOTTOM_TO_TOP,
        )

    @class_cached_property
    @classmethod
    def SMOLENSK(cls) -> "HLLMap":
        return cls(
            id="smolensk",
            name="SMOLENSK",
            tag="SMO",
            year=1941,
            pretty_name="Smolensk",
            short_name="Smolensk",
            allies=HLLFaction.SOV,
            axis=HLLFaction.GER,
            allies_direction=CardinalDirection.RIGHT_TO_LEFT,
        )

    @class_cached_property
    @classmethod
    def ST_MARIE_DU_MONT(cls) -> "HLLMap":
        return cls(
            id="stmariedumont",
            name="ST MARIE DU MONT",
            tag="SMDM",
            year=1944,
            pretty_name="St. Marie Du Mont",
            short_name="SMDM",
            allies=HLLFaction.US,
            axis=HLLFaction.GER,
            allies_direction=CardinalDirection.BOTTOM_TO_TOP,
        )

    @class_cached_property
    @classmethod
    def ST_MERE_EGLISE(cls) -> "HLLMap":
        return cls(
            id="stmereeglise",
            name="SAINTE-MÈRE-ÉGLISE",
            tag="SME",
            year=1944,
            pretty_name="St. Mere Eglise",
            short_name="SME",
            allies=HLLFaction.US,
            axis=HLLFaction.GER,
            allies_direction=CardinalDirection.RIGHT_TO_LEFT,
        )

    @class_cached_property
    @classmethod
    def STALINGRAD(cls) -> "HLLMap":
        return cls(
            id="stalingrad",
            name="STALINGRAD",
            tag="STA",
            year=1942,
            pretty_name="Stalingrad",
            short_name="Stalingrad",
            allies=HLLFaction.SOV,
            axis=HLLFaction.GER,
            allies_direction=CardinalDirection.RIGHT_TO_LEFT,
        )

    @class_cached_property
    @classmethod
    def TOBRUK(cls) -> "HLLMap":
        return cls(
            id="tobruk",
            name="TOBRUK",
            tag="TBK",
            year=1942,
            pretty_name="Tobruk",
            short_name="Tobruk",
            allies=HLLFaction.B8A,
            axis=HLLFaction.DAK,
            allies_direction=CardinalDirection.RIGHT_TO_LEFT,
        )

    @class_cached_property
    @classmethod
    def UTAH_BEACH(cls) -> "HLLMap":
        return cls(
            id="utahbeach",
            name="UTAH BEACH",
            tag="UTA",
            year=1944,
            pretty_name="Utah Beach",
            short_name="Utah",
            allies=HLLFaction.US,
            axis=HLLFaction.GER,
            allies_direction=CardinalDirection.RIGHT_TO_LEFT,
        )


class HLLVMap(_Map[HLLVFaction]):
    @class_cached_property
    @classmethod
    def THANH_HOA_BRIDGE(cls) -> "HLLVMap":
        return cls(
            id="wdevf",
            name="THANH HÒA BRIDGE",
            tag="THA",
            year=1965,
            pretty_name="Thanh Hòa Bridge",
            short_name="Thanh Hoa",
            allies=HLLVFaction.US,
            axis=HLLVFaction.NVA,
            allies_direction=CardinalDirection.BOTTOM_TO_TOP,
        )


Map: TypeAlias = HLLMap | HLLVMap
