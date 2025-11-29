# ruff: noqa: N802

from enum import StrEnum

from ._utils import (
    CaseInsensitiveIndexedBaseModel,
    class_cached_property,
)
from .factions import Faction


class Orientation(StrEnum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class Map(CaseInsensitiveIndexedBaseModel):
    name: str
    tag: str
    pretty_name: str
    short_name: str
    allies: Faction
    axis: Faction
    orientation: Orientation
    """Whether the sectors on this map are stacked horizontally (left-to-right) or
    vertically (top-to-bottom)."""
    mirror_factions: bool
    """If the side each faction starts at is mirrored or not. By default, Allies spawn
    left/top, Axis spawn right/bottom."""

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id!r}, name={self.name!r}, "
            f"tag={self.tag!r}, pretty_name={self.pretty_name!r}, "
            f"short_name={self.short_name!r}, allies={self.allies!r}, "
            f"axis={self.axis!r}, orientation={self.orientation!r}, "
            f"mirror_factions={self.mirror_factions!r})"
        )

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (Map, str)):
            return str(self).lower() == str(other).lower()
        return NotImplemented

    @class_cached_property
    @classmethod
    def CARENTAN(cls) -> "Map":
        return cls(
            id="carentan",
            name="CARENTAN",
            tag="CAR",
            pretty_name="Carentan",
            short_name="Carentan",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.HORIZONTAL,
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def DRIEL(cls) -> "Map":
        return cls(
            id="driel",
            name="DRIEL",
            tag="DRL",
            pretty_name="Driel",
            short_name="Driel",
            allies=Faction.CW,
            axis=Faction.GER,
            orientation=Orientation.VERTICAL,
            mirror_factions=True,
        )

    @class_cached_property
    @classmethod
    def EL_ALAMEIN(cls) -> "Map":
        return cls(
            id="elalamein",
            name="EL ALAMEIN",
            tag="ELA",
            pretty_name="El Alamein",
            short_name="Alamein",
            allies=Faction.B8A,
            axis=Faction.DAK,
            orientation=Orientation.HORIZONTAL,
            mirror_factions=True,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_RIDGE(cls) -> "Map":
        return cls(
            id="elsenbornridge",
            name="ELSENBORN RIDGE",
            tag="EBR",
            pretty_name="Elsenborn Ridge",
            short_name="Elsenborn",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.VERTICAL,
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def FOY(cls) -> "Map":
        return cls(
            id="foy",
            name="FOY",
            tag="FOY",
            pretty_name="Foy",
            short_name="Foy",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.VERTICAL,
            mirror_factions=True,
        )

    @class_cached_property
    @classmethod
    def HILL_400(cls) -> "Map":
        return cls(
            id="hill400",
            name="HILL 400",
            tag="HIL",
            pretty_name="Hill 400",
            short_name="Hill 400",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.HORIZONTAL,
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def HURTGEN_FOREST(cls) -> "Map":
        return cls(
            id="hurtgenforest",
            name="HÜRTGEN FOREST",
            tag="HUR",
            pretty_name="Hurtgen Forest",
            short_name="Hurtgen",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.HORIZONTAL,
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def KHARKOV(cls) -> "Map":
        return cls(
            id="kharkov",
            name="Kharkov",
            tag="KHA",
            pretty_name="Kharkov",
            short_name="Kharkov",
            allies=Faction.SOV,
            axis=Faction.GER,
            orientation=Orientation.VERTICAL,
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def KURSK(cls) -> "Map":
        return cls(
            id="kursk",
            name="KURSK",
            tag="KUR",
            pretty_name="Kursk",
            short_name="Kursk",
            allies=Faction.SOV,
            axis=Faction.GER,
            orientation=Orientation.VERTICAL,
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def MORTAIN(cls) -> "Map":
        return cls(
            id="mortain",
            name="MORTAIN",
            tag="MOR",
            pretty_name="Mortain",
            short_name="Mortain",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.HORIZONTAL,
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def OMAHA_BEACH(cls) -> "Map":
        return cls(
            id="omahabeach",
            name="OMAHA BEACH",
            tag="OMA",
            pretty_name="Omaha Beach",
            short_name="Omaha",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.HORIZONTAL,
            mirror_factions=True,
        )

    @class_cached_property
    @classmethod
    def PURPLE_HEART_LANE(cls) -> "Map":
        return cls(
            id="purpleheartlane",
            name="PURPLE HEART LANE",
            tag="PHL",
            pretty_name="Purple Heart Lane",
            short_name="PHL",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.VERTICAL,
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def REMAGEN(cls) -> "Map":
        return cls(
            id="remagen",
            name="REMAGEN",
            tag="REM",
            pretty_name="Remagen",
            short_name="Remagen",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.VERTICAL,
            mirror_factions=True,
        )

    @class_cached_property
    @classmethod
    def SMOLENSK(cls) -> "Map":
        return cls(
            id="smolensk",
            name="SMOLENSK",
            tag="SMO",
            pretty_name="Smolensk",
            short_name="Smolensk",
            allies=Faction.SOV,
            axis=Faction.GER,
            orientation=Orientation.HORIZONTAL,
            mirror_factions=True,
        )

    @class_cached_property
    @classmethod
    def ST_MARIE_DU_MONT(cls) -> "Map":
        return cls(
            id="stmariedumont",
            name="ST MARIE DU MONT",
            tag="SMDM",
            pretty_name="St. Marie Du Mont",
            short_name="SMDM",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.VERTICAL,
            mirror_factions=False,
        )

    @class_cached_property
    @classmethod
    def ST_MERE_EGLISE(cls) -> "Map":
        return cls(
            id="stmereeglise",
            name="SAINTE-MÈRE-ÉGLISE",
            tag="SME",
            pretty_name="St. Mere Eglise",
            short_name="SME",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.HORIZONTAL,
            mirror_factions=True,
        )

    @class_cached_property
    @classmethod
    def STALINGRAD(cls) -> "Map":
        return cls(
            id="stalingrad",
            name="STALINGRAD",
            tag="STA",
            pretty_name="Stalingrad",
            short_name="Stalingrad",
            allies=Faction.SOV,
            axis=Faction.GER,
            orientation=Orientation.HORIZONTAL,
            mirror_factions=True,
        )

    @class_cached_property
    @classmethod
    def TOBRUK(cls) -> "Map":
        return cls(
            id="tobruk",
            name="TOBRUK",
            tag="TBK",
            pretty_name="Tobruk",
            short_name="Tobruk",
            allies=Faction.B8A,
            axis=Faction.DAK,
            orientation=Orientation.HORIZONTAL,
            mirror_factions=True,
        )

    @class_cached_property
    @classmethod
    def UTAH_BEACH(cls) -> "Map":
        return cls(
            id="utahbeach",
            name="UTAH BEACH",
            tag="UTA",
            pretty_name="Utah Beach",
            short_name="Utah",
            allies=Faction.US,
            axis=Faction.GER,
            orientation=Orientation.HORIZONTAL,
            mirror_factions=True,
        )
