from enum import Enum, StrEnum

from hllrcon.data import factions
from hllrcon.data.utils import IndexedBaseModel


class Orientation(StrEnum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class Environment(str, Enum):
    DAWN = "dawn"
    DAY = "day"
    DUSK = "dusk"
    NIGHT = "night"
    OVERCAST = "overcast"
    RAIN = "rain"


class Map(IndexedBaseModel[str]):
    name: str
    tag: str
    pretty_name: str
    short_name: str
    allies: factions.Faction
    axis: factions.Faction
    orientation: Orientation
    mirrored: bool
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
            f"mirrored={self.mirrored!r})"
        )

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (Map, str)):
            return str(self).lower() == str(other).lower()
        return NotImplemented


ST_MERE_EGLISE = Map(
    id="stmereeglise",
    name="SAINTE-MÈRE-ÉGLISE",
    tag="SME",
    pretty_name="St. Mere Eglise",
    short_name="SME",
    allies=factions.US,
    axis=factions.GER,
    orientation=Orientation.HORIZONTAL,
    mirrored=True,
)
ST_MARIE_DU_MONT = Map(
    id="stmariedumont",
    name="ST MARIE DU MONT",
    tag="SMDM",
    pretty_name="St. Marie Du Mont",
    short_name="SMDM",
    allies=factions.US,
    axis=factions.GER,
    orientation=Orientation.VERTICAL,
    mirrored=False,
)
UTAH_BEACH = Map(
    id="utahbeach",
    name="UTAH BEACH",
    tag="UTA",
    pretty_name="Utah Beach",
    short_name="Utah",
    allies=factions.US,
    axis=factions.GER,
    orientation=Orientation.HORIZONTAL,
    mirrored=True,
)
OMAHA_BEACH = Map(
    id="omahabeach",
    name="OMAHA BEACH",
    tag="OMA",
    pretty_name="Omaha Beach",
    short_name="Omaha",
    allies=factions.US,
    axis=factions.GER,
    orientation=Orientation.HORIZONTAL,
    mirrored=True,
)
PURPLE_HEART_LANE = Map(
    id="purpleheartlane",
    name="PURPLE HEART LANE",
    tag="PHL",
    pretty_name="Purple Heart Lane",
    short_name="PHL",
    allies=factions.US,
    axis=factions.GER,
    orientation=Orientation.VERTICAL,
    mirrored=False,
)
CARENTAN = Map(
    id="carentan",
    name="CARENTAN",
    tag="CAR",
    pretty_name="Carentan",
    short_name="Carentan",
    allies=factions.US,
    axis=factions.GER,
    orientation=Orientation.HORIZONTAL,
    mirrored=False,
)
HURTGEN_FOREST = Map(
    id="hurtgenforest",
    name="HÜRTGEN FOREST",
    tag="HUR",
    pretty_name="Hurtgen Forest",
    short_name="Hurtgen",
    allies=factions.US,
    axis=factions.GER,
    orientation=Orientation.HORIZONTAL,
    mirrored=False,
)
HILL_400 = Map(
    id="hill400",
    name="HILL 400",
    tag="HIL",
    pretty_name="Hill 400",
    short_name="Hill 400",
    allies=factions.US,
    axis=factions.GER,
    orientation=Orientation.HORIZONTAL,
    mirrored=False,
)
FOY = Map(
    id="foy",
    name="FOY",
    tag="FOY",
    pretty_name="Foy",
    short_name="Foy",
    allies=factions.US,
    axis=factions.GER,
    orientation=Orientation.VERTICAL,
    mirrored=True,
)
KURSK = Map(
    id="kursk",
    name="KURSK",
    tag="KUR",
    pretty_name="Kursk",
    short_name="Kursk",
    allies=factions.SOV,
    axis=factions.GER,
    orientation=Orientation.VERTICAL,
    mirrored=False,
)
STALINGRAD = Map(
    id="stalingrad",
    name="STALINGRAD",
    tag="STA",
    pretty_name="Stalingrad",
    short_name="Stalingrad",
    allies=factions.SOV,
    axis=factions.GER,
    orientation=Orientation.HORIZONTAL,
    mirrored=True,
)
REMAGEN = Map(
    id="remagen",
    name="REMAGEN",
    tag="REM",
    pretty_name="Remagen",
    short_name="Remagen",
    allies=factions.US,
    axis=factions.GER,
    orientation=Orientation.VERTICAL,
    mirrored=True,
)
KHARKOV = Map(
    id="kharkov",
    name="Kharkov",
    tag="KHA",
    pretty_name="Kharkov",
    short_name="Kharkov",
    allies=factions.SOV,
    axis=factions.GER,
    orientation=Orientation.VERTICAL,
    mirrored=False,
)
DRIEL = Map(
    id="driel",
    name="DRIEL",
    tag="DRL",
    pretty_name="Driel",
    short_name="Driel",
    allies=factions.GB,
    axis=factions.GER,
    orientation=Orientation.VERTICAL,
    mirrored=True,
)
EL_ALAMEIN = Map(
    id="elalamein",
    name="EL ALAMEIN",
    tag="ELA",
    pretty_name="El Alamein",
    short_name="Alamein",
    allies=factions.B8A,
    axis=factions.DAK,
    orientation=Orientation.HORIZONTAL,
    mirrored=True,
)
MORTAIN = Map(
    id="mortain",
    name="MORTAIN",
    tag="MOR",
    pretty_name="Mortain",
    short_name="Mortain",
    allies=factions.US,
    axis=factions.GER,
    orientation=Orientation.HORIZONTAL,
    mirrored=False,
)
ELSENBORN_RIDGE = Map(
    id="elsenbornridge",
    name="ELSENBORN RIDGE",
    tag="EBR",
    pretty_name="Elsenborn Ridge",
    short_name="Elsenborn",
    allies=factions.US,
    axis=factions.GER,
    orientation=Orientation.VERTICAL,
    mirrored=False,
)
TOBRUK = Map(
    id="tobruk",
    name="TOBRUK",
    tag="TBK",
    pretty_name="Tobruk",
    short_name="Tobruk",
    allies=factions.B8A,
    axis=factions.DAK,
    orientation=Orientation.HORIZONTAL,
    mirrored=True,
)


def by_id(map_id: str) -> Map:
    return Map.by_id(map_id)
