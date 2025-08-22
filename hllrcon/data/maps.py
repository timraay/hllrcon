# ruff: noqa: N802

from collections.abc import Generator
from enum import StrEnum
from typing import Self, overload

from pydantic import BaseModel, RootModel, model_validator

from ._utils import (
    CaseInsensitiveIndexedBaseModel,
    class_cached_property,
)
from .factions import Faction


class Orientation(StrEnum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class Strongpoint(BaseModel, frozen=True):
    name: str
    center: tuple[float, float, float]
    radius: float

    def is_inside(self, pos: tuple[float, float, float]) -> bool:
        """Check whether a given position is inside the strongpoint.

        Parameters
        ----------
        pos : tuple[float, float, float]
            The position to check.

        Returns
        -------
        bool
            True if the position is inside the strongpoint, False otherwise.

        """
        dx = pos[0] - self.center[0]
        dy = pos[1] - self.center[1]
        dz = pos[2] - self.center[2]
        return dx * dx + dy * dy + dz * dz <= self.radius * self.radius


class Sector(BaseModel, frozen=True):
    """A sector is a 400x400m area on the map containing a strongpoint."""

    grid_pos: tuple[int, int]
    """If the map were divided into 5x5 grid, at which position this sector would be
    located."""
    strongpoint: Strongpoint

    def is_inside(self, pos: tuple[float, float] | tuple[float, float, float]) -> bool:
        """Check whether a given position is inside the sector.

        Parameters
        ----------
        pos : tuple[float, float]
            The position to check

        Returns
        -------
        bool
            True if the position is inside the sector, False otherwise.

        """
        x = round(pos[0] / 40000) + 2
        y = round(pos[1] / 40000) + 2
        return (x, y) == self.grid_pos


class SectorRow(RootModel[tuple[Sector, Sector, Sector]], frozen=True):
    """A sector row is a row of three sectors on the map."""

    def __init__(
        self,
        sector1: Sector,
        sector2: Sector,
        sector3: Sector,
    ) -> None:
        super().__init__((sector1, sector2, sector3))

    def __iter__(self) -> Generator[Sector]:  # type: ignore[override]
        yield from self.root

    def __getitem__(self, index: int) -> Sector:
        return self.root[index]

    def is_inside(self, pos: tuple[float, float] | tuple[float, float, float]) -> bool:
        """Check whether a given position is inside the sector row.

        Parameters
        ----------
        pos : tuple[float, float]
            The position to check

        Returns
        -------
        bool
            True if the position is inside the sector row, False otherwise.

        """
        return any(sector.is_inside(pos) for sector in self)


class Sectors(
    RootModel[tuple[SectorRow, SectorRow, SectorRow, SectorRow, SectorRow]],
    frozen=True,
):
    """A collection of all five sector rows on the map."""

    def __init__(
        self,
        sector_row1: SectorRow,
        sector_row2: SectorRow,
        sector_row3: SectorRow,
        sector_row4: SectorRow,
        sector_row5: SectorRow,
    ) -> None:
        super().__init__(
            (sector_row1, sector_row2, sector_row3, sector_row4, sector_row5),
        )

    def __iter__(self) -> Generator[SectorRow]:  # type: ignore[override]
        yield from self.root

    @overload
    def __getitem__(self, index: int) -> SectorRow: ...

    @overload
    def __getitem__(self, index: tuple[int, int]) -> Sector: ...

    def __getitem__(self, index: int | tuple[int, int]) -> SectorRow | Sector:
        if isinstance(index, tuple) and len(index) == 2:
            return self.root[index[0]][index[1]]
        return self.root[index]


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
    sectors: Sectors
    """The five sectors available on the map for Warfare and Offensive game modes.
    Sectors run from left to right or top to bottom, depending on the orientation of
    the map."""
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

    @model_validator(mode="after")
    def _validate_sector_grid_pos(self) -> Self:
        for row_idx, sector_row in enumerate(self.sectors):
            for sector_idx, sector in enumerate(sector_row):
                err_msg = f"Invalid sector grid position: {sector.grid_pos}"
                if (
                    self.orientation == Orientation.HORIZONTAL
                    and sector.grid_pos != (row_idx, sector_idx + 1)
                ) or (
                    self.orientation == Orientation.VERTICAL
                    and sector.grid_pos != (sector_idx + 1, row_idx)
                ):
                    raise ValueError(err_msg)
        return self

    def get_sector_at_pos(self, pos: tuple[float, float]) -> Sector | None:
        """Get the sector at the position, if any.

        Parameters
        ----------
        pos : tuple[float, float]
            The position to check.

        Returns
        -------
        Sector | None
            The sector, or None if out of bounds.

        """
        col = round(pos[0] / 40000) + 2
        row = round(pos[1] / 40000) + 2

        if self.orientation == Orientation.HORIZONTAL:
            if 0 <= col < 5 and 1 <= row < 4:
                return self.sectors[col][row - 1]
            return None

        if self.orientation == Orientation.VERTICAL:
            if 1 <= col < 4 and 0 <= row < 5:
                return self.sectors[row][col - 1]
            return None

        return None  # pragma: no cover

    def get_sector_row_at_pos(self, pos: tuple[float, float]) -> SectorRow | None:
        """Get the sector row at the position, if any.

        The position does not have to be strictly within the row, as the boundary
        extends infinitely along the axis of the row. To confirm whether a position
        is also in bounds, check `SectorRow.is_inside(pos)` after.

        Parameters
        ----------
        pos : tuple[float, float]
            The position to check.

        Returns
        -------
        SectorRow | None
            The sector row, or None if out of bounds.

        """
        if self.orientation == Orientation.HORIZONTAL:
            x = pos[0]
        elif self.orientation == Orientation.VERTICAL:
            x = pos[1]
        else:  # pragma: no cover
            return None

        row = round(x / 40000) + 2
        if 0 <= row < 5:
            return self.sectors[row]

        return None

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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(0, 1),
                        strongpoint=Strongpoint(
                            name="Blactot",
                            center=(-65543.41, -39731.965, 1359.9531),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 2),
                        strongpoint=Strongpoint(
                            name="502nd Start",
                            center=(-67076.41, 4670.035, 123.953125),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 3),
                        strongpoint=Strongpoint(
                            name="Farm Ruins",
                            center=(-68814.41, 37720.035, 365.95312),
                            radius=5000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="Pumping Station",
                            center=(-36748.406, -29821.965, 146.95312),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="Ruins",
                            center=(-26183.406, 2343.0352, 101.953125),
                            radius=3000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="Derailed Train",
                            center=(-39381.406, 28975.035, 279.95312),
                            radius=5000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="Canal Crossing",
                            center=(5892.5938, -39387.965, 279.95312),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="Town Center",
                            center=(1021.59375, -1021.96484, 104.953125),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="Train Station",
                            center=(246.59375, 27698.035, 176.95312),
                            radius=5000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="Customs",
                            center=(40816.594, -34224.965, 279.95312),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="Rail Crossing",
                            center=(44171.594, -6296.965, 279.95312),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="Mount Halais",
                            center=(33828.594, 51343.035, 2518.9531),
                            radius=3973.6313,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(4, 1),
                        strongpoint=Strongpoint(
                            name="Canal Locks",
                            center=(66826.59, -26456.965, 279.95312),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 2),
                        strongpoint=Strongpoint(
                            name="Rail Causeway",
                            center=(75611.59, 5968.035, 279.95312),
                            radius=5495.63,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 3),
                        strongpoint=Strongpoint(
                            name="La Maison Des Ormes",
                            center=(72222.59, 38476.035, 103.53516),
                            radius=5000.0,
                        ),
                    ),
                ),
            ),
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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(1, 0),
                        strongpoint=Strongpoint(
                            name="Oosterbeek Approach",
                            center=(-36028.543, -79955.25, -412.13928),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 0),
                        strongpoint=Strongpoint(
                            name="Roseander Polder",
                            center=(2809.0745, -78795.875, -159.22235),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 0),
                        strongpoint=Strongpoint(
                            name="Kasteel Rosande",
                            center=(38371.14, -76418.7, 86.83746),
                            radius=7000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="Boatyard",
                            center=(-38518.715, -33980.625, -205.24878),
                            radius=7000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="Bridgeway",
                            center=(3880.9673, -39449.43, -249.79703),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="Rijn Banks",
                            center=(39177.535, -42960.49, -309.9341),
                            radius=7000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="Brick Factory",
                            center=(-39703.027, 6122.7656, -205.24878),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="Railway Bridge",
                            center=(2882.3755, -3877.2988, -205.24878),
                            radius=9000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="Gun Emplacements",
                            center=(43301.99, -2530.0012, -205.24878),
                            radius=5500.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="Rietveld",
                            center=(-40615.844, 40909.707, -375.4043),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="South Railway",
                            center=(3826.8418, 42206.754, -429.63922),
                            radius=8000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="Middel Road",
                            center=(41461.46, 38457.824, -205.24878),
                            radius=6000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 4),
                        strongpoint=Strongpoint(
                            name="Orchards",
                            center=(-39533.195, 77266.98, -329.62988),
                            radius=8000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 4),
                        strongpoint=Strongpoint(
                            name="Schaduwwolken Farm",
                            center=(-2113.1738, 75816.06, -357.01),
                            radius=6500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 4),
                        strongpoint=Strongpoint(
                            name="Fields",
                            center=(41461.46, 75453.516, -205.25464),
                            radius=6000.0,
                        ),
                    ),
                ),
            ),
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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(0, 1),
                        strongpoint=Strongpoint(
                            name="Vehicle Depot",
                            center=(-68233.38, -37264.52, 968.23914),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 2),
                        strongpoint=Strongpoint(
                            name="Artillery Guns",
                            center=(-71609.83, -8175.4565, -228.91907),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 3),
                        strongpoint=Strongpoint(
                            name="Miteiriya Ridge",
                            center=(-79261.695, 36680.625, 1629.1664),
                            radius=6000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="Hamlet Ruins",
                            center=(-37466.633, -37732.38, -1402.2225),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="El Mreir",
                            center=(-37776.816, -2887.5278, -1248.4254),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="Watchtower",
                            center=(-40818.59, 37838.586, 648.23755),
                            radius=6000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="Desert Rat Trenches",
                            center=(4880.006, -40988.05, 831.8468),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="Oasis",
                            center=(-2900.921, -851.27783, -1248.4254),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="Valley",
                            center=(1970.4421, 35186.074, -787.2982),
                            radius=8190.72,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="Fuel Depot",
                            center=(43333.848, -35426.484, -1862.4927),
                            radius=7000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="Airfield Command",
                            center=(38495.92, -4155.8906, -1057.3627),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="Airfield Hangars",
                            center=(41085.367, 32927.33, -1248.4176),
                            radius=8000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(4, 1),
                        strongpoint=Strongpoint(
                            name="Cliffside Village",
                            center=(68942.24, -39028.402, 550.42114),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 2),
                        strongpoint=Strongpoint(
                            name="Ambushed Convoy",
                            center=(72480.45, -2526.4434, -1248.4176),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 3),
                        strongpoint=Strongpoint(
                            name="Quarry",
                            center=(78760.73, 41540.4, -69.86389),
                            radius=6000.0,
                        ),
                    ),
                ),
            ),
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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(1, 0),
                        strongpoint=Strongpoint(
                            name="99th Command Centre",
                            center=(-39637.496, -67610.96, 5383.203),
                            radius=7500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 0),
                        strongpoint=Strongpoint(
                            name="Gun Battery",
                            center=(420.0, -69376.0, 6308.203),
                            radius=8000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 0),
                        strongpoint=Strongpoint(
                            name="U.S. Camp",
                            center=(50979.016, -67675.0, 6308.203),
                            radius=7000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="Elsenborn Ridge",
                            center=(-30950.0, -41967.96, 6858.203),
                            radius=7000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="Farahilde Farm",
                            center=(10158.0, -30210.0, 5808.203),
                            radius=8000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="Jensit Pillboxes",
                            center=(49674.99, -28085.947, 5108.2026),
                            radius=7000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="Road To Elsenborn Ridge",
                            center=(-40964.0, 3317.0, 6608.203),
                            radius=8000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="Dug Out Tank",
                            center=(-9124.0, 2404.0, 5608.203),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="Checkpoint",
                            center=(40444.914, 6529.1445, 1716.1997),
                            radius=5000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="Erelsdell Farmhouse",
                            center=(-41672.0, 38246.0, 3633.2031),
                            radius=8000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="AA Battery",
                            center=(8607.678, 33127.07, 2796.5845),
                            radius=7000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="Hinterburg",
                            center=(39637.227, 39888.688, 3225.2002),
                            radius=8000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 4),
                        strongpoint=Strongpoint(
                            name="Supply Cache",
                            center=(-25666.0, 66300.0, 2862.2031),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 4),
                        strongpoint=Strongpoint(
                            name="Foxholes",
                            center=(12223.855, 67172.27, -364.80078),
                            radius=7000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 4),
                        strongpoint=Strongpoint(
                            name="Fuel Depot",
                            center=(38049.76, 70408.04, 2951.984),
                            radius=7000.0,
                        ),
                    ),
                ),
            ),
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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(1, 0),
                        strongpoint=Strongpoint(
                            name="Road To Recogne",
                            center=(-49755.0, -74340.0, -211.0),
                            radius=2750.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 0),
                        strongpoint=Strongpoint(
                            name="Cobru Approach",
                            center=(9952.0, -74787.0, -243.0),
                            radius=3500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 0),
                        strongpoint=Strongpoint(
                            name="Road To Noville",
                            center=(38286.176, -76947.95, -243.0),
                            radius=5343.75,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="Cobru Factory",
                            center=(-29988.0, -44676.0, -890.0),
                            radius=5500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="Foy",
                            center=(-9586.0, -34052.0, -551.0),
                            radius=3250.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="Flak Battery",
                            center=(45241.0, -39594.0, -964.0),
                            radius=4000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="West Bend",
                            center=(-53153.0, -12966.0, -634.0),
                            radius=5500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="Southern Edge",
                            center=(-1114.0, 589.0, -102.0),
                            radius=4738.37,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="Dugout Barn",
                            center=(46085.04, -4721.094, -1008.08936),
                            radius=4139.884,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="N30 Highway",
                            center=(-38407.0, 31775.0, -142.0),
                            radius=6250.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="Bizory Foy Road",
                            center=(10035.0, 39390.0, -545.0),
                            radius=3500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="Eastern Ourthe",
                            center=(45845.0, 27822.0, -771.0),
                            radius=4531.25,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 4),
                        strongpoint=Strongpoint(
                            name="Road To Bastogne",
                            center=(-52862.0, 63773.0, 112.0),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 4),
                        strongpoint=Strongpoint(
                            name="Bois Jacques",
                            center=(-5582.0, 68237.0, 1106.0),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 4),
                        strongpoint=Strongpoint(
                            name="Forest Outskirts",
                            center=(46279.0, 67141.0, 512.0),
                            radius=5000.0,
                        ),
                    ),
                ),
            ),
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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(0, 1),
                        strongpoint=Strongpoint(
                            name="Convoy Ambush",
                            center=(-65875.18, -36966.816, 6207.824),
                            radius=3000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 2),
                        strongpoint=Strongpoint(
                            name="Federchecke Junction",
                            center=(-65367.926, 2874.167, 10826.176),
                            radius=4250.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 3),
                        strongpoint=Strongpoint(
                            name="Stuckchen Farm",
                            center=(-63938.484, 42413.004, 8142.296),
                            radius=3000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="Roer River House",
                            center=(-38405.066, -43380.766, -342.3706),
                            radius=3000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="Bergstein Church",
                            center=(-30580.357, 8420.501, 11575.116),
                            radius=3000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="Kirchweg",
                            center=(-41257.29, 31282.14, 8949.19),
                            radius=3000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="Flak Pits",
                            center=(1384.4886, -33584.805, 8937.715),
                            radius=3000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="Hill 400",
                            center=(-1408.8995, 4698.0444, 17213.738),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="Southern Approach",
                            center=(948.21277, 25170.994, 12086.199),
                            radius=3000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="Eselsweg Junction",
                            center=(26549.63, -41028.504, 7713.7764),
                            radius=3000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="Eastern Slope",
                            center=(29662.375, -3406.8445, 8725.453),
                            radius=3000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="Trainwreck",
                            center=(32129.537, 43600.098, 994.9547),
                            radius=3000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(4, 1),
                        strongpoint=Strongpoint(
                            name="Roer River Crossing",
                            center=(64685.836, -33321.977, -2164.823),
                            radius=3000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 2),
                        strongpoint=Strongpoint(
                            name="Zerkall",
                            center=(78823.555, -9569.677, -2095.891),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 3),
                        strongpoint=Strongpoint(
                            name="PaperMill",
                            center=(69319.79, 39032.61, -2095.891),
                            radius=3000.0,
                        ),
                    ),
                ),
            ),
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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(0, 1),
                        strongpoint=Strongpoint(
                            name="The Masbauch Approach",
                            center=(-74423.0, -46733.0, 4336.0),
                            radius=4625.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 2),
                        strongpoint=Strongpoint(
                            name="Reserve Station",
                            center=(-78776.0, 2238.0, 3895.0),
                            radius=4500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 3),
                        strongpoint=Strongpoint(
                            name="Lumber Yard",
                            center=(-77356.0, 36029.0, 4122.0),
                            radius=4000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="Wehebach Overlook",
                            center=(-38278.0, -34416.0, 6683.0),
                            radius=5031.25,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="Kall Trail",
                            center=(-35755.0, 2459.0, 4007.0),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="The Ruin",
                            center=(-42793.0, 26141.0, 3879.0),
                            radius=4400.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="North Pass",
                            center=(6540.0, -49329.0, 215.0),
                            radius=4347.4674749999995,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="The Scar",
                            center=(-6935.0, 3328.0, 1327.0),
                            radius=3015.2502,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="The Siegfried Line",
                            center=(-3711.0, 42305.0, 2603.0),
                            radius=4500.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="Hill 15",
                            center=(45628.0, -34330.0, 4504.0),
                            radius=-4500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="Jacob's Barn",
                            center=(37658.0, 8531.0, 6550.0),
                            radius=3500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="Salient 42",
                            center=(40632.0, 50244.0, 6895.0),
                            radius=3250.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(4, 1),
                        strongpoint=Strongpoint(
                            name="Grosshau Approach",
                            center=(73663.0, -38895.0, 5297.0),
                            radius=3750.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 2),
                        strongpoint=Strongpoint(
                            name="Hürtgen Approach",
                            center=(67776.0, 6558.0, 6600.0),
                            radius=3500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 3),
                        strongpoint=Strongpoint(
                            name="Logging Camp",
                            center=(64477.0, 51502.0, 6495.0),
                            radius=3750.0,
                        ),
                    ),
                ),
            ),
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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(1, 0),
                        strongpoint=Strongpoint(
                            name="Marsh Town",
                            center=(-36517.52, -70661.75, -2300.2422),
                            radius=3750.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 0),
                        strongpoint=Strongpoint(
                            name="Soviet Vantage Point",
                            center=(8032.91, -70714.63, 402.14062),
                            radius=3750.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 0),
                        strongpoint=Strongpoint(
                            name="German Fuel Dump",
                            center=(41168.312, -70231.15, 3192.4492),
                            radius=3750.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="Bitter Spring",
                            center=(-37433.285, -38891.406, -2293.7441),
                            radius=8000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="Lumber Works",
                            center=(7916.1367, -39814.156, 279.73047),
                            radius=3750.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="Windmill Hillside",
                            center=(46877.23, -41370.87, 2556.1875),
                            radius=3750.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="Water Mill",
                            center=(-36761.05, -3563.8867, -2120.2441),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="St Mary",
                            center=(6074.9873, -633.23, 911.6289),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="Distillery",
                            center=(44449.215, -4542.487, 2724.1992),
                            radius=3750.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="River Crossing",
                            center=(-27116.355, 40003.023, -890.95703),
                            radius=3750.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="Belgorod Outskirts",
                            center=(8105.9688, 38673.008, 221.38281),
                            radius=9000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="Lumberyard",
                            center=(46774.79, 37490.91, 2052.8438),
                            radius=3750.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 4),
                        strongpoint=Strongpoint(
                            name="Wehrmacht Overlook",
                            center=(-37313.91, 72972.37, -661.0508),
                            radius=3750.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 4),
                        strongpoint=Strongpoint(
                            name="Hay Storage",
                            center=(4240.6523, 71736.38, -1926.957),
                            radius=3750.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 4),
                        strongpoint=Strongpoint(
                            name="Overpass",
                            center=(41180.39, 70416.95, -41.4375),
                            radius=3750.0,
                        ),
                    ),
                ),
            ),
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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(1, 0),
                        strongpoint=Strongpoint(
                            name="Artillery Position",
                            center=(-35117.0, -68921.0, 9323.0),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 0),
                        strongpoint=Strongpoint(
                            name="Grushki",
                            center=(7070.0, -68141.0, 7093.0),
                            radius=4960.5308,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 0),
                        strongpoint=Strongpoint(
                            name="Grushki Flank",
                            center=(47151.0, -67169.0, 5786.0),
                            radius=4500.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="Panzer's End",
                            center=(-35117.0, -31958.0, 8935.0),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="Defence In Depth",
                            center=(1604.0, -34906.0, 7647.0),
                            radius=7022.2216,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="Listening Post",
                            center=(40413.0, -36000.0, 5889.0),
                            radius=7673.426,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="The Windmills",
                            center=(-26712.39, -4842.251, 9948.998),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="Yamki",
                            center=(9609.0, 3974.0, 8754.0),
                            radius=6973.061,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="Oleg's House",
                            center=(39754.0, 7774.0, 6623.0),
                            radius=4500.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="Rudno",
                            center=(-27089.0, 40069.0, 9949.0),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="Destroyed Battery",
                            center=(-990.0, 39981.0, 10190.0),
                            radius=4500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="The Muddy Churn",
                            center=(41089.0, 42772.0, 7983.0),
                            radius=4500.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 4),
                        strongpoint=Strongpoint(
                            name="Road To Kursk",
                            center=(-31287.0, 68120.0, 9949.0),
                            radius=4500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 4),
                        strongpoint=Strongpoint(
                            name="Ammo Dump",
                            center=(-1729.0, 66294.0, 9632.0),
                            radius=5446.865,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 4),
                        strongpoint=Strongpoint(
                            name="Eastern Position",
                            center=(36100.0, 65758.0, 8227.0),
                            radius=6000.0,
                        ),
                    ),
                ),
            ),
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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(0, 1),
                        strongpoint=Strongpoint(
                            name="Hotel De La Poste",
                            center=(-71664.03, -47217.445, -480.30115),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 2),
                        strongpoint=Strongpoint(
                            name="Forward Battery",
                            center=(-67949.4, 6438.873, -978.4287),
                            radius=6500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 3),
                        strongpoint=Strongpoint(
                            name="Southern Approach",
                            center=(-70344.09, 46402.33, -5391.659),
                            radius=7500.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="Mortain Outskirts",
                            center=(-49136.977, -39819.566, 1842.5009),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="Forward Medical Aid Station",
                            center=(-35275.574, -2194.1567, 2411.5898),
                            radius=7000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="Mortain Approach",
                            center=(-42775.5, 33050.027, -1580.7439),
                            radius=7000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="Hill 314",
                            center=(-2425.1055, -38259.5, 5891.1714),
                            radius=7000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="Petit Chappelle Saint Michel",
                            center=(1725.2772, 5918.17, 5670.377),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="U.S. Southern Roadblock",
                            center=(-11254.05, 49076.438, -3064.87),
                            radius=7000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="Destroyed German Convoy",
                            center=(35469.836, -42255.99, 6050.5566),
                            radius=8000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="German Recon Camp",
                            center=(40439.145, -2510.7285, 4398.437),
                            radius=6000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="Le Hermitage Farm",
                            center=(48018.547, 26619.574, 1071.811),
                            radius=6000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(4, 1),
                        strongpoint=Strongpoint(
                            name="Abandoned German Checkpoint",
                            center=(68651.26, -40271.47, 6068.428),
                            radius=6500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 2),
                        strongpoint=Strongpoint(
                            name="German Defensive Camp",
                            center=(68294.46, 1986.8845, 3941.4448),
                            radius=7000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 3),
                        strongpoint=Strongpoint(
                            name="Farm Of Bonovisin",
                            center=(71327.67, 36841.695, 1896.9764),
                            radius=7000.0,
                        ),
                    ),
                ),
            ),
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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(0, 1),
                        strongpoint=Strongpoint(
                            name="Beaumont Road",
                            center=(-66508.0, -34528.0, 1461.6543),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 2),
                        strongpoint=Strongpoint(
                            name="Crossroads",
                            center=(-63975.723, 2684.23, 1607.7931),
                            radius=3713.8135,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 3),
                        strongpoint=Strongpoint(
                            name="Les Isles",
                            center=(-65785.0, 33673.0, 1949.5156),
                            radius=5000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="Rear Battery",
                            center=(-40364.508, -47019.88, 1471.3027),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="Church Road",
                            center=(-36692.0, -9308.0, 1471.3047),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="The Orchards",
                            center=(-44319.355, 27163.912, 1705.2588),
                            radius=4000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="West Vierville",
                            center=(4665.0, -40540.0, 1262.0),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="Vierville Sur Mer",
                            center=(-2661.8896, -2895.0942, 889.7754),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="Artillery Battery",
                            center=(2342.277, 31510.633, 1730.7812),
                            radius=5000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="WN73",
                            center=(54259.0, -44498.0, 164.8125),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="WN71",
                            center=(55132.387, -5791.973, 1015.4961),
                            radius=3750.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="WN70",
                            center=(46516.0, 30340.0, 1368.2734),
                            radius=5000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(4, 1),
                        strongpoint=Strongpoint(
                            name="Dog Green",
                            center=(67602.0, -31262.0, -3134.6387),
                            radius=6250.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 2),
                        strongpoint=Strongpoint(
                            name="The Draw",
                            center=(71322.0, -7432.0, -2748.504),
                            radius=3750.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 3),
                        strongpoint=Strongpoint(
                            name="Dog White",
                            center=(71817.0, 30284.0, -3019.504),
                            radius=5000.0,
                        ),
                    ),
                ),
            ),
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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(1, 0),
                        strongpoint=Strongpoint(
                            name="Bloody Bend",
                            center=(-53699.133, -68803.984, 6831.375),
                            radius=2750.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 0),
                        strongpoint=Strongpoint(
                            name="Dead Man's Corner",
                            center=(740.8672, -65433.984, 6831.375),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 0),
                        strongpoint=Strongpoint(
                            name="Forward Battery",
                            center=(33330.867, -66643.984, 6831.375),
                            radius=4000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="Jourdan Canal",
                            center=(-41489.133, -38108.99, 6831.375),
                            radius=2750.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="Douve Bridge",
                            center=(-1434.0474, -26826.268, 7010.586),
                            radius=4250.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="Douve River Battery",
                            center=(33572.38, -36601.72, 6840.3447),
                            radius=3500.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="Groult Pillbox",
                            center=(-37607.4, -5672.991, 6730.6123),
                            radius=5500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="Carentan Causeway",
                            center=(787.74744, 1346.289, 6969.521),
                            radius=3500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="Flak Position",
                            center=(45592.906, -4116.6772, 6732.951),
                            radius=-4750.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="Madeleine Farm",
                            center=(-33264.676, 30204.594, 7391.552),
                            radius=3250.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="Madeleine Bridge",
                            center=(1928.2188, 39878.098, 6973.26),
                            radius=3000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="Aid Station",
                            center=(47043.207, 32172.8, 6753.122),
                            radius=3250.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 4),
                        strongpoint=Strongpoint(
                            name="Ingouf Crossroads",
                            center=(-36344.676, 66489.59, 7391.552),
                            radius=3250.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 4),
                        strongpoint=Strongpoint(
                            name="Road To Carentan",
                            center=(2953.2188, 63908.098, 6973.26),
                            radius=3000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 4),
                        strongpoint=Strongpoint(
                            name="Cabbage Patch",
                            center=(46253.22, 62363.098, 6973.26),
                            radius=2500.0,
                        ),
                    ),
                ),
            ),
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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(1, 0),
                        strongpoint=Strongpoint(
                            name="Alte Liebe Barsch",
                            center=(-41114.0, -69583.0, 6515.0),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 0),
                        strongpoint=Strongpoint(
                            name="Bewaldet Kreuzung",
                            center=(-891.0, -69550.0, 12708.0),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 0),
                        strongpoint=Strongpoint(
                            name="Dan Radart 512",
                            center=(41625.0, -69063.0, 16150.0),
                            radius=4000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="Erpel",
                            center=(-39275.0, -40853.0, 1774.0),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="Erpeler Ley",
                            center=(9697.0, -42679.0, 13960.0),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="Kasbach Outlook",
                            center=(38436.418, -41098.23, 9033.0),
                            radius=4000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="St Severin Chapel",
                            center=(-39275.0, -12967.0, 766.0),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="Ludendorff Bridge",
                            center=(3032.2412, 7.0210953, 1261.005),
                            radius=8000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="Bauernhof Am Rhein",
                            center=(38817.02, 15613.944, 104.0),
                            radius=4000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="Remagen",
                            center=(-35925.75, 39434.0, -27.363525),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="Mobelfabrik",
                            center=(-1000.0, 40824.0, -35.674072),
                            radius=5000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="SchlieffenAusweg",
                            center=(39053.0, 38264.0, 104.0),
                            radius=4000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 4),
                        strongpoint=Strongpoint(
                            name="Waldburg",
                            center=(-40954.977, 80279.71, -125.40869),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 4),
                        strongpoint=Strongpoint(
                            name="Muhlenweg",
                            center=(3742.6152, 72094.91, -121.5036),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 4),
                        strongpoint=Strongpoint(
                            name="Hagelkreuz",
                            center=(37607.746, 68933.32, 104.0),
                            radius=4000.0,
                        ),
                    ),
                ),
            ),
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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(1, 0),
                        strongpoint=Strongpoint(
                            name="Winters Landing",
                            center=(-39503.258, -78343.03, 809.0),
                            radius=5754.7485,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 0),
                        strongpoint=Strongpoint(
                            name="Le Grand Chemin",
                            center=(-367.0, -76667.0, 809.0),
                            radius=4500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 0),
                        strongpoint=Strongpoint(
                            name="The Barn",
                            center=(44896.0, -73822.0, -89.0),
                            radius=5691.033,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="Brecourt Battery",
                            center=(-39380.0, -39702.0, 809.0),
                            radius=6078.6405,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="Cattlesheds",
                            center=(2961.319, -41557.402, 809.0),
                            radius=5400.8775,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="Rue De La Gare",
                            center=(35565.562, -39370.594, 809.0),
                            radius=5892.7635,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="The Dugout",
                            center=(-37170.906, -151.18701, 460.30884),
                            radius=5814.819,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="AA Network",
                            center=(1716.0, 2530.0, 422.64746),
                            radius=6530.8635,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="Pierre's Farm",
                            center=(37508.1, 1336.6963, 438.40137),
                            radius=5207.283,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="Hugo's Farm",
                            center=(-38001.0, 38089.0, 809.0),
                            radius=6046.29,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="The Hamlet",
                            center=(-2158.7668, 42649.312, 597.02246),
                            radius=4500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="Ste Marie Du Mont",
                            center=(47022.125, 50258.56, 1336.7599),
                            radius=6000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 4),
                        strongpoint=Strongpoint(
                            name="The Corner",
                            center=(-34620.76, 69152.766, 809.0),
                            radius=5105.9565,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 4),
                        strongpoint=Strongpoint(
                            name="Hill 6",
                            center=(142.14453, 76822.93, 467.88086),
                            radius=4500.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 4),
                        strongpoint=Strongpoint(
                            name="The Fields",
                            center=(39750.15, 78234.78, 1152.4478),
                            radius=4500.0,
                        ),
                    ),
                ),
            ),
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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(0, 1),
                        strongpoint=Strongpoint(
                            name="Flak Position",
                            center=(-69311.0, -40772.0, -81.0),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 2),
                        strongpoint=Strongpoint(
                            name="Vaulaville",
                            center=(-62223.0, -3146.0, -1163.0),
                            radius=2507.38,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 3),
                        strongpoint=Strongpoint(
                            name="La Prairie",
                            center=(-67517.0, 35037.0, 1050.0),
                            radius=4000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="Route Du Haras",
                            center=(-40886.0, -37779.0, -688.63086),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="Western Approach",
                            center=(-32652.0, -14761.0, -400.0),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="Rue De Gambosville",
                            center=(-34553.0, 41733.0, -699.0),
                            radius=4000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="Hospice",
                            center=(-1100.0, -46000.0, -400.0),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="Ste Mere Eglise",
                            center=(5949.0, -7436.0, -718.7539),
                            radius=4741.136,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="Checkpoint",
                            center=(467.0, 32490.0, -1330.0),
                            radius=4000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="Artillery Battery",
                            center=(39652.0, -34374.0, -400.0),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="The Cemetery",
                            center=(28858.0, 5593.0, -742.64844),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="Maison Du Crique",
                            center=(25884.0, 30530.0, -400.0),
                            radius=4000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(4, 1),
                        strongpoint=Strongpoint(
                            name="Les Vieux Vergers",
                            center=(70168.0, -28861.0, -743.6719),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 2),
                        strongpoint=Strongpoint(
                            name="Cross Roads",
                            center=(72279.0, 1393.0, -676.0),
                            radius=4000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 3),
                        strongpoint=Strongpoint(
                            name="Russeau De Ferme",
                            center=(72138.0, 38912.0, -1125.0),
                            radius=4000.0,
                        ),
                    ),
                ),
            ),
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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(0, 1),
                        strongpoint=Strongpoint(
                            name="Mamayev Approach",
                            center=(-65790.0, -47756.0, 5954.0),
                            radius=6535.388,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 2),
                        strongpoint=Strongpoint(
                            name="Nail Factory",
                            center=(-66906.0, 11138.0, 7515.0),
                            radius=7094.4257,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 3),
                        strongpoint=Strongpoint(
                            name="City Overlook",
                            center=(-66906.0, 50137.0, 7445.0),
                            radius=7094.426,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="Dolgiy Ravine",
                            center=(-33041.0, -54925.0, 3965.0),
                            radius=4625.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="Yellow House",
                            center=(-40433.438, 2798.4553, 7515.0),
                            radius=5882.1836,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="Komsomol HQ",
                            center=(-41553.0, 41896.0, 7310.0),
                            radius=7094.426,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="Railway Crossing",
                            center=(-1763.0, -41563.0, 3965.0),
                            radius=4625.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="Carriage Depot",
                            center=(6505.0, 173.0, 4961.0),
                            radius=7094.426,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="Train Station",
                            center=(-1824.0, 34468.0, 4942.0),
                            radius=7094.426,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="House Of The Workers",
                            center=(31861.0, -43662.0, 3965.0),
                            radius=4153.8267,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="Pavlov's House",
                            center=(51236.0, -868.0, 3965.0),
                            radius=4625.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="The Brewery",
                            center=(42954.0, 44100.0, 4127.0),
                            radius=4985.413,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(4, 1),
                        strongpoint=Strongpoint(
                            name="L Shaped House",
                            center=(68445.0, -34613.0, 3965.0),
                            radius=4625.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 2),
                        strongpoint=Strongpoint(
                            name="Grudinin's Mill",
                            center=(68703.0, -1282.0, 3965.0),
                            radius=4406.25,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 3),
                        strongpoint=Strongpoint(
                            name="Volga Banks",
                            center=(70121.0, 43351.0, 3965.0),
                            radius=5514.2393,
                        ),
                    ),
                ),
            ),
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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(0, 1),
                        strongpoint=Strongpoint(
                            name="Guard Room",
                            center=(-68855.0, -27530.0, -6107.8867),
                            radius=7000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 2),
                        strongpoint=Strongpoint(
                            name="Tank Graveyard",
                            center=(-69405.0, -2075.0, -7493.6714),
                            radius=8000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 3),
                        strongpoint=Strongpoint(
                            name="Division Headquarters",
                            center=(-69835.0, 45005.0, -8821.878),
                            radius=7000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="West Creek",
                            center=(-40077.0, -44015.0, -5846.329),
                            radius=8000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="Albergo Ristorante Moderno",
                            center=(-29536.549, 2241.0, -7323.1304),
                            radius=7000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="King Square",
                            center=(-29485.152, 39744.316, -7213.4697),
                            radius=8000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="Desert Rat Caves",
                            center=(31.221313, -39665.25, -5381.714),
                            radius=8000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="Church Grounds",
                            center=(59.92363, 11770.049, -7002.9688),
                            radius=7000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="Admiralty House",
                            center=(7919.4326, 48901.832, -7326.4785),
                            radius=9000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="Abandoned Ammo Cache",
                            center=(39687.508, -39659.996, -4662.4526),
                            radius=8000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="8th Army Medical Hospital",
                            center=(40124.035, -2845.0, -7074.448),
                            radius=9000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="Supply Drop",
                            center=(39820.547, 43918.36, -7314.533),
                            radius=9000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(4, 1),
                        strongpoint=Strongpoint(
                            name="Road To Senussi Mine",
                            center=(69522.8, -40790.0, -4568.7607),
                            radius=7000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 2),
                        strongpoint=Strongpoint(
                            name="Makeshift Aid Station",
                            center=(69380.0, 25.0, -6849.7656),
                            radius=9000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 3),
                        strongpoint=Strongpoint(
                            name="Cargo Warehouses",
                            center=(70047.33, 41171.96, -7616.6694),
                            radius=8000.0,
                        ),
                    ),
                ),
            ),
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
            sectors=Sectors(
                SectorRow(
                    Sector(
                        grid_pos=(0, 1),
                        strongpoint=Strongpoint(
                            name="Mammut Radar",
                            center=(-65158.0, -51522.0, -2401.0),
                            radius=3000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 2),
                        strongpoint=Strongpoint(
                            name="Flooded House",
                            center=(-66464.0, -2944.0, -2388.0),
                            radius=3000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(0, 3),
                        strongpoint=Strongpoint(
                            name="Sainte Marie Approach",
                            center=(-64837.0, 52705.0, -2157.0),
                            radius=3000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(1, 1),
                        strongpoint=Strongpoint(
                            name="Sunken Bridge",
                            center=(-30810.0, -47853.0, -2157.0),
                            radius=3000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 2),
                        strongpoint=Strongpoint(
                            name="La Grande Crique",
                            center=(-28986.0, 508.0, -2388.0),
                            radius=3294.095,
                        ),
                    ),
                    Sector(
                        grid_pos=(1, 3),
                        strongpoint=Strongpoint(
                            name="Drowned Fields",
                            center=(-36400.0, 43928.0, -2157.0),
                            radius=3000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(2, 1),
                        strongpoint=Strongpoint(
                            name="WN4",
                            center=(5359.0, -42267.0, -2283.0),
                            radius=3742.354,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 2),
                        strongpoint=Strongpoint(
                            name="The Chapel",
                            center=(10650.0, -7786.0, -2157.0),
                            radius=3000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(2, 3),
                        strongpoint=Strongpoint(
                            name="WN7",
                            center=(727.0, 50408.0, -2157.0),
                            radius=5000.0,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(3, 1),
                        strongpoint=Strongpoint(
                            name="AABattery",
                            center=(35101.0, -43589.0, -2389.0),
                            radius=3941.9941,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 2),
                        strongpoint=Strongpoint(
                            name="Hill 5",
                            center=(36131.0, -1838.0, -2157.0),
                            radius=3000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(3, 3),
                        strongpoint=Strongpoint(
                            name="WN5",
                            center=(48763.0, 44080.0, -2247.0),
                            radius=3194.091,
                        ),
                    ),
                ),
                SectorRow(
                    Sector(
                        grid_pos=(4, 1),
                        strongpoint=Strongpoint(
                            name="Tare Green",
                            center=(63845.0, -46581.0, -2284.0),
                            radius=3000.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 2),
                        strongpoint=Strongpoint(
                            name="Red Roof House",
                            center=(64923.67, 3144.1865, -2206.6382),
                            radius=3250.0,
                        ),
                    ),
                    Sector(
                        grid_pos=(4, 3),
                        strongpoint=Strongpoint(
                            name="Uncle Red",
                            center=(66675.0, 45162.0, -2157.0),
                            radius=2823.963,
                        ),
                    ),
                ),
            ),
            mirror_factions=True,
        )
