import math
from typing import TYPE_CHECKING, Self

from pydantic import BaseModel, PrivateAttr, model_validator

from hllrcon.data.maps import Orientation

if TYPE_CHECKING:
    from hllrcon.data.layers import Layer

GridPos = tuple[int, int]
GridArea = tuple[GridPos, GridPos]
WorldPos2D = tuple[float, float]
WorldPos3D = tuple[float, float, float]
WorldArea2D = tuple[WorldPos2D, WorldPos2D]


class Grid(BaseModel, frozen=True):
    scale: float
    offset: WorldPos2D
    size: GridArea

    @classmethod
    def large(
        cls,
        *,
        scale: float = 20000.0,
        offset: WorldPos2D = (0.0, 0.0),
        size: GridArea = ((-5, -5), (4, 4)),
    ) -> Self:
        return cls(
            scale=scale,
            offset=offset,
            size=size,
        )

    @classmethod
    def small(
        cls,
        *,
        scale: float = 13926.4,
        offset: WorldPos2D = (0.0, 0.0),
        size: GridArea = ((-5, -5), (4, 4)),
    ) -> Self:
        return cls(
            scale=scale,
            offset=offset,
            size=size,
        )

    def grid_to_world_from(self, grid_pos: GridPos) -> WorldPos2D:
        x = grid_pos[0] * self.scale + self.offset[0]
        y = grid_pos[1] * self.scale + self.offset[1]
        return (x, y)

    def grid_to_world_to(self, grid_pos: GridPos) -> WorldPos2D:
        x = (grid_pos[0] + 1) * self.scale + self.offset[0]
        y = (grid_pos[1] + 1) * self.scale + self.offset[1]
        return (x, y)

    def world_to_grid(self, world_pos: WorldPos2D) -> GridPos:
        x = (world_pos[0] - self.offset[0]) / self.scale
        y = (world_pos[1] - self.offset[1]) / self.scale
        return (math.floor(x), math.floor(y))


class GridPositionalModel(BaseModel, frozen=True):
    _layer: "Layer" = PrivateAttr()
    grid_from: GridPos
    grid_to: GridPos

    @model_validator(mode="after")
    def _validate_grid_from_to_order(self) -> Self:
        if self.grid_from[0] > self.grid_to[0] or self.grid_from[1] > self.grid_to[1]:
            msg = "grid_from must be smaller than grid_to"
            raise ValueError(msg)
        return self

    @property
    def from_(self) -> WorldPos2D:
        return self._layer.grid.grid_to_world_from(self.grid_from)

    @property
    def to(self) -> WorldPos2D:
        return self._layer.grid.grid_to_world_to(self.grid_to)

    @property
    def area(self) -> WorldArea2D:
        return (self.from_, self.to)

    def is_inside(self, world_pos: WorldPos2D) -> bool:
        x1, y1 = self.from_
        x2, y2 = self.to
        px, py = world_pos
        return x1 <= px <= x2 and y1 <= py <= y2


class Strongpoint(BaseModel, frozen=True):
    id: str
    name: str
    center: WorldPos3D
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


class CaptureZone(GridPositionalModel, frozen=True):
    strongpoint: Strongpoint


class Sector(GridPositionalModel, frozen=True):
    capture_zones: list[CaptureZone]

    @classmethod
    def large_layout(
        cls,
        orientation: Orientation,
        strongpoints: tuple[
            tuple[Strongpoint, Strongpoint, Strongpoint],
            tuple[Strongpoint, Strongpoint, Strongpoint],
            tuple[Strongpoint, Strongpoint, Strongpoint],
            tuple[Strongpoint, Strongpoint, Strongpoint],
            tuple[Strongpoint, Strongpoint, Strongpoint],
        ],
    ) -> list[Self]:
        if orientation == Orientation.HORIZONTAL:

            def orient(x: int, y: int) -> tuple[int, int]:
                return x, y
        else:

            def orient(x: int, y: int) -> tuple[int, int]:
                return y, x

        return [
            cls(
                grid_from=orient(2 * i - 5, -3),
                grid_to=orient(2 * i - 4, 2),
                capture_zones=[
                    CaptureZone(
                        grid_from=orient(2 * i - 5, 2 * j - 3),
                        grid_to=orient(2 * i - 4, 2 * j - 2),
                        strongpoint=strongpoint,
                    )
                    for j, strongpoint in enumerate(sector)
                ],
            )
            for i, sector in enumerate(strongpoints)
        ]

    @classmethod
    def skirmish_layout(
        cls,
        orientation: Orientation,
        strongpoint: Strongpoint,
    ) -> list[Self]:
        if orientation == Orientation.HORIZONTAL:

            def orient(x: int, y: int) -> tuple[int, int]:
                return x, y
        else:

            def orient(x: int, y: int) -> tuple[int, int]:
                return y, x

        return [
            cls(
                grid_from=orient(-5, -4),
                grid_to=orient(-2, 3),
                capture_zones=[],
            ),
            cls(
                grid_from=orient(-1, -4),
                grid_to=orient(0, 3),
                capture_zones=[
                    CaptureZone(
                        grid_from=orient(-1, -1),
                        grid_to=orient(0, 0),
                        strongpoint=strongpoint,
                    ),
                ],
            ),
            cls(
                grid_from=orient(1, -4),
                grid_to=orient(4, 3),
                capture_zones=[],
            ),
        ]


SECTORS_CARENTAN_LARGE = Sector.large_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoints=(
        (
            Strongpoint(
                id="BLACTOT",
                name="Blactot",
                center=(-65543.41, -39731.965, 1359.9531),
                radius=5000.0,
            ),
            Strongpoint(
                id="502ND START",
                name="502nd Start",
                center=(-67076.41, 4670.035, 123.953125),
                radius=5000.0,
            ),
            Strongpoint(
                id="FARM RUINS",
                name="Farm Ruins",
                center=(-68814.41, 37720.035, 365.95312),
                radius=5000.0,
            ),
        ),
        (
            Strongpoint(
                id="PUMPING STATION",
                name="Pumping Station",
                center=(-36748.406, -29821.965, 146.95312),
                radius=5000.0,
            ),
            Strongpoint(
                id="RUINS",
                name="Ruins",
                center=(-26183.406, 2343.0352, 101.953125),
                radius=3000.0,
            ),
            Strongpoint(
                id="DERAILED TRAIN",
                name="Derailed Train",
                center=(-39381.406, 28975.035, 279.95312),
                radius=5000.0,
            ),
        ),
        (
            Strongpoint(
                id="CANAL CROSSING",
                name="Canal Crossing",
                center=(5892.5938, -39387.965, 279.95312),
                radius=5000.0,
            ),
            Strongpoint(
                id="TOWN CENTER",
                name="Town Center",
                center=(1021.59375, -1021.96484, 104.953125),
                radius=5000.0,
            ),
            Strongpoint(
                id="TRAIN STATION",
                name="Train Station",
                center=(246.59375, 27698.035, 176.95312),
                radius=5000.0,
            ),
        ),
        (
            Strongpoint(
                id="CUSTOMS",
                name="Customs",
                center=(40816.594, -34224.965, 279.95312),
                radius=5000.0,
            ),
            Strongpoint(
                id="RAIL CROSSING",
                name="Rail Crossing",
                center=(44171.594, -6296.965, 279.95312),
                radius=5000.0,
            ),
            Strongpoint(
                id="MONT HALAIS",
                name="Mount Halais",
                center=(33828.594, 51343.035, 2518.9531),
                radius=3973.6313,
            ),
        ),
        (
            Strongpoint(
                id="CANAL LOCKS",
                name="Canal Locks",
                center=(66826.59, -26456.965, 279.95312),
                radius=5000.0,
            ),
            Strongpoint(
                id="RAIL CAUSEWAY",
                name="Rail Causeway",
                center=(75611.59, 5968.035, 279.95312),
                radius=5495.63,
            ),
            Strongpoint(
                id="LA MAISON DES ORMES",
                name="La Maison Des Ormes",
                center=(72222.59, 38476.035, 103.53516),
                radius=5000.0,
            ),
        ),
    ),
)

SECTORS_CARENTAN_SMALL = Sector.skirmish_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoint=Strongpoint(
        id="Town Center",
        name="Town Center",
        center=(60.0, 160.0, -850.0),
        radius=8000.0,
    ),
)

SECTORS_DRIEL_LARGE = Sector.large_layout(
    orientation=Orientation.VERTICAL,
    strongpoints=(
        (
            Strongpoint(
                id="OOSTERBEEK APPROACH",
                name="Oosterbeek Approach",
                center=(-36028.543, -79955.25, -412.13928),
                radius=6000.0,
            ),
            Strongpoint(
                id="ROSANDER POLDER",
                name="Roseander Polder",
                center=(2809.0745, -78795.875, -159.22235),
                radius=6000.0,
            ),
            Strongpoint(
                id="KASTEEL ROSANDE",
                name="Kasteel Rosande",
                center=(38371.14, -76418.7, 86.83746),
                radius=7000.0,
            ),
        ),
        (
            Strongpoint(
                id="BOATYARD",
                name="Boatyard",
                center=(-38518.715, -33980.625, -205.24878),
                radius=7000.0,
            ),
            Strongpoint(
                id="BRIDGEWAY",
                name="Bridgeway",
                center=(3880.9673, -39449.43, -249.79703),
                radius=6000.0,
            ),
            Strongpoint(
                id="RIJN BANKS",
                name="Rijn Banks",
                center=(39177.535, -42960.49, -309.9341),
                radius=7000.0,
            ),
        ),
        (
            Strongpoint(
                id="BRICK FACTORY",
                name="Brick Factory",
                center=(-39703.027, 6122.7656, -205.24878),
                radius=6000.0,
            ),
            Strongpoint(
                id="RAILWAY BRIDGE",
                name="Railway Bridge",
                center=(2882.3755, -3877.2988, -205.24878),
                radius=9000.0,
            ),
            Strongpoint(
                id="GUN EMPLACEMENTS",
                name="Gun Emplacements",
                center=(43301.99, -2530.0012, -205.24878),
                radius=5500.0,
            ),
        ),
        (
            Strongpoint(
                id="RIETVELD",
                name="Rietveld",
                center=(-40615.844, 40909.707, -375.4043),
                radius=6000.0,
            ),
            Strongpoint(
                id="SOUTH RAILWAY",
                name="South Railway",
                center=(3826.8418, 42206.754, -429.63922),
                radius=8000.0,
            ),
            Strongpoint(
                id="MIDDEL ROAD",
                name="Middel Road",
                center=(41461.46, 38457.824, -205.24878),
                radius=6000.0,
            ),
        ),
        (
            Strongpoint(
                id="ORCHARDS",
                name="Orchards",
                center=(-39533.195, 77266.98, -329.62988),
                radius=8000.0,
            ),
            Strongpoint(
                id="SCHADUWWOLKEN FARM",
                name="Schaduwwolken Farm",
                center=(-2113.1738, 75816.06, -357.01),
                radius=6500.0,
            ),
            Strongpoint(
                id="FIELDS",
                name="Fields",
                center=(41461.46, 75453.516, -205.25464),
                radius=6000.0,
            ),
        ),
    ),
)

SECTORS_DRIEL_SMALL = Sector.skirmish_layout(
    orientation=Orientation.VERTICAL,
    strongpoint=Strongpoint(
        id="UNDERPASS",
        name="Underpass",
        center=(2600.0, -750.0, 450.0),
        radius=8000.0,
    ),
)

SECTORS_ELALAMEIN_LARGE = Sector.large_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoints=(
        (
            Strongpoint(
                id="VEHICLE DEPOT",
                name="Vehicle Depot",
                center=(-68233.38, -37264.52, 968.23914),
                radius=6000.0,
            ),
            Strongpoint(
                id="ARTILLERY GUNS",
                name="Artillery Guns",
                center=(-71609.83, -8175.4565, -228.91907),
                radius=6000.0,
            ),
            Strongpoint(
                id="MITEIRIYA RIDGE",
                name="Miteiriya Ridge",
                center=(-79261.695, 36680.625, 1629.1664),
                radius=6000.0,
            ),
        ),
        (
            Strongpoint(
                id="HAMLET RUINS",
                name="Hamlet Ruins",
                center=(-37466.633, -37732.38, -1402.2225),
                radius=6000.0,
            ),
            Strongpoint(
                id="EL MREIR",
                name="El Mreir",
                center=(-37776.816, -2887.5278, -1248.4254),
                radius=6000.0,
            ),
            Strongpoint(
                id="WATCHTOWER",
                name="Watchtower",
                center=(-40818.59, 37838.586, 648.23755),
                radius=6000.0,
            ),
        ),
        (
            Strongpoint(
                id="DESERT RAT TRENCHES",
                name="Desert Rat Trenches",
                center=(4880.006, -40988.05, 831.8468),
                radius=6000.0,
            ),
            Strongpoint(
                id="OASIS",
                name="Oasis",
                center=(-2900.921, -851.27783, -1248.4254),
                radius=6000.0,
            ),
            Strongpoint(
                id="VALLEY",
                name="Valley",
                center=(1970.4421, 35186.074, -787.2982),
                radius=8190.72,
            ),
        ),
        (
            Strongpoint(
                id="FUEL DEPOT",
                name="Fuel Depot",
                center=(43333.848, -35426.484, -1862.4927),
                radius=7000.0,
            ),
            Strongpoint(
                id="AIRFIELD COMMAND",
                name="Airfield Command",
                center=(38495.92, -4155.8906, -1057.3627),
                radius=6000.0,
            ),
            Strongpoint(
                id="AIRFIELD HANGARS",
                name="Airfield Hangars",
                center=(41085.367, 32927.33, -1248.4176),
                radius=8000.0,
            ),
        ),
        (
            Strongpoint(
                id="CLIFFSIDE VILLAGE",
                name="Cliffside Village",
                center=(68942.24, -39028.402, 550.42114),
                radius=6000.0,
            ),
            Strongpoint(
                id="AMBUSHED CONVOY",
                name="Ambushed Convoy",
                center=(72480.45, -2526.4434, -1248.4176),
                radius=6000.0,
            ),
            Strongpoint(
                id="QUARRY",
                name="Quarry",
                center=(78760.73, 41540.4, -69.86389),
                radius=6000.0,
            ),
        ),
    ),
)

SECTORS_ELALAMEIN_SMALL = Sector.skirmish_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoint=Strongpoint(
        id="OASIS",
        name="Oasis",
        center=(-171.79688, -4065.439, -850.0),
        radius=6000.0,
    ),
)

SECTORS_ELSENBORNRIDGE_LARGE = Sector.large_layout(
    orientation=Orientation.VERTICAL,
    strongpoints=(
        (
            Strongpoint(
                id="99TH COMMAND CENTRE",
                name="99th Command Centre",
                center=(-39637.496, -67610.96, 5383.203),
                radius=7500.0,
            ),
            Strongpoint(
                id="GUN BATTERY",
                name="Gun Battery",
                center=(420.0, -69376.0, 6308.203),
                radius=8000.0,
            ),
            Strongpoint(
                id="U.S. CAMP",
                name="U.S. Camp",
                center=(50979.016, -67675.0, 6308.203),
                radius=7000.0,
            ),
        ),
        (
            Strongpoint(
                id="ELSENBORN RIDGE",
                name="Elsenborn Ridge",
                center=(-30950.0, -41967.96, 6858.203),
                radius=7000.0,
            ),
            Strongpoint(
                id="FARAHILDE FARM",
                name="Farahilde Farm",
                center=(10158.0, -30210.0, 5808.203),
                radius=8000.0,
            ),
            Strongpoint(
                id="JENSIT PILLBOXES",
                name="Jensit Pillboxes",
                center=(49674.99, -28085.947, 5108.2026),
                radius=7000.0,
            ),
        ),
        (
            Strongpoint(
                id="ROAD TO ELSENBORN RIDGE",
                name="Road To Elsenborn Ridge",
                center=(-40964.0, 3317.0, 6608.203),
                radius=8000.0,
            ),
            Strongpoint(
                id="DUGOUT TANKS",
                name="Dug Out Tank",
                center=(-9124.0, 2404.0, 5608.203),
                radius=6000.0,
            ),
            Strongpoint(
                id="CHECKPOINT",
                name="Checkpoint",
                center=(40444.914, 6529.1445, 1716.1997),
                radius=5000.0,
            ),
        ),
        (
            Strongpoint(
                id="ERELSDELL FARMHOUSE",
                name="Erelsdell Farmhouse",
                center=(-41672.0, 38246.0, 3633.2031),
                radius=8000.0,
            ),
            Strongpoint(
                id="AA BATTERY",
                name="AA Battery",
                center=(8607.678, 33127.07, 2796.5845),
                radius=7000.0,
            ),
            Strongpoint(
                id="HINTERBERG",
                name="Hinterburg",
                center=(39637.227, 39888.688, 3225.2002),
                radius=8000.0,
            ),
        ),
        (
            Strongpoint(
                id="SUPPLY CACHE",
                name="Supply Cache",
                center=(-25666.0, 66300.0, 2862.2031),
                radius=5000.0,
            ),
            Strongpoint(
                id="FOXHOLES",
                name="Foxholes",
                center=(12223.855, 67172.27, -364.80078),
                radius=7000.0,
            ),
            Strongpoint(
                id="FUEL DEPOT",
                name="Fuel Depot",
                center=(38049.76, 70408.04, 2951.984),
                radius=7000.0,
            ),
        ),
    ),
)

SECTORS_ELSENBORNRIDGE_SMALL = Sector.skirmish_layout(
    orientation=Orientation.VERTICAL,
    strongpoint=Strongpoint(
        id="DUG OUT TANK",
        name="Dug Out Tank",
        center=(-8510.0, 1410.0, -279.18115),
        radius=5000.0,
    ),
)

SECTORS_FOY_LARGE = Sector.large_layout(
    orientation=Orientation.VERTICAL,
    strongpoints=(
        (
            Strongpoint(
                id="ROAD TO RECOGNE",
                name="Road To Recogne",
                center=(-49755.0, -74340.0, -211.0),
                radius=2750.0,
            ),
            Strongpoint(
                id="COBRU APPROACH",
                name="Cobru Approach",
                center=(9952.0, -74787.0, -243.0),
                radius=3500.0,
            ),
            Strongpoint(
                id="ROAD TO NOVILLE",
                name="Road To Noville",
                center=(38286.176, -76947.95, -243.0),
                radius=5343.75,
            ),
        ),
        (
            Strongpoint(
                id="COBRU FACTORY",
                name="Cobru Factory",
                center=(-29988.0, -44676.0, -890.0),
                radius=5500.0,
            ),
            Strongpoint(
                id="FOY",
                name="Foy",
                center=(-9586.0, -34052.0, -551.0),
                radius=3250.0,
            ),
            Strongpoint(
                id="FLAK BATTERY",
                name="Flak Battery",
                center=(45241.0, -39594.0, -964.0),
                radius=4000.0,
            ),
        ),
        (
            Strongpoint(
                id="WEST BEND",
                name="West Bend",
                center=(-53153.0, -12966.0, -634.0),
                radius=5500.0,
            ),
            Strongpoint(
                id="SOUTHERN EDGE",
                name="Southern Edge",
                center=(-1114.0, 589.0, -102.0),
                radius=4738.37,
            ),
            Strongpoint(
                id="DUGOUT BARN",
                name="Dugout Barn",
                center=(46085.04, -4721.094, -1008.08936),
                radius=4139.884,
            ),
        ),
        (
            Strongpoint(
                id="N30 HIGHWAY",
                name="N30 Highway",
                center=(-38407.0, 31775.0, -142.0),
                radius=6250.0,
            ),
            Strongpoint(
                id="BIZORY-FOY ROAD",
                name="Bizory-Foy Road",
                center=(10035.0, 39390.0, -545.0),
                radius=3500.0,
            ),
            Strongpoint(
                id="EASTERN OURTHE",
                name="Eastern Ourthe",
                center=(45845.0, 27822.0, -771.0),
                radius=4531.25,
            ),
        ),
        (
            Strongpoint(
                id="ROAD TO BASTOGNE",
                name="Road To Bastogne",
                center=(-52862.0, 63773.0, 112.0),
                radius=4000.0,
            ),
            Strongpoint(
                id="BOIS JACQUES",
                name="Bois Jacques",
                center=(-5582.0, 68237.0, 1106.0),
                radius=5000.0,
            ),
            Strongpoint(
                id="FOREST OUTSKIRTS",
                name="Forest Outskirts",
                center=(46279.0, 67141.0, 512.0),
                radius=5000.0,
            ),
        ),
    ),
)

SECTORS_HILL400_LARGE = Sector.large_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoints=(
        (
            Strongpoint(
                id="CONVOY AMBUSH",
                name="Convoy Ambush",
                center=(-65875.18, -36966.816, 6207.824),
                radius=3000.0,
            ),
            Strongpoint(
                id="FEDERHECKE JUNCTION",
                name="Federchecke Junction",
                center=(-65367.926, 2874.167, 10826.176),
                radius=4250.0,
            ),
            Strongpoint(
                id="STUCKCHEN FARM",
                name="Stuckchen Farm",
                center=(-63938.484, 42413.004, 8142.296),
                radius=3000.0,
            ),
        ),
        (
            Strongpoint(
                id="ROER RIVER HOUSE",
                name="Roer River House",
                center=(-38405.066, -43380.766, -342.3706),
                radius=3000.0,
            ),
            Strongpoint(
                id="BERGSTEIN CHURCH",
                name="Bergstein Church",
                center=(-30580.357, 8420.501, 11575.116),
                radius=3000.0,
            ),
            Strongpoint(
                id="KIRCHWEG",
                name="Kirchweg",
                center=(-41257.29, 31282.14, 8949.19),
                radius=3000.0,
            ),
        ),
        (
            Strongpoint(
                id="FLAK PITS",
                name="Flak Pits",
                center=(1384.4886, -33584.805, 8937.715),
                radius=3000.0,
            ),
            Strongpoint(
                id="HILL 400",
                name="Hill 400",
                center=(-1408.8995, 4698.0444, 17213.738),
                radius=5000.0,
            ),
            Strongpoint(
                id="SOUTHERN APPROACH",
                name="Southern Approach",
                center=(948.21277, 25170.994, 12086.199),
                radius=3000.0,
            ),
        ),
        (
            Strongpoint(
                id="ESELSWEG JUNCTION",
                name="Eselsweg Junction",
                center=(26549.63, -41028.504, 7713.7764),
                radius=3000.0,
            ),
            Strongpoint(
                id="EASTERN SLOPE",
                name="Eastern Slope",
                center=(29662.375, -3406.8445, 8725.453),
                radius=3000.0,
            ),
            Strongpoint(
                id="TRAIN WRECK",
                name="Trainwreck",
                center=(32129.537, 43600.098, 994.9547),
                radius=3000.0,
            ),
        ),
        (
            Strongpoint(
                id="ROER RIVER CROSSING",
                name="Roer River Crossing",
                center=(64685.836, -33321.977, -2164.823),
                radius=3000.0,
            ),
            Strongpoint(
                id="ZERKALL",
                name="Zerkall",
                center=(78823.555, -9569.677, -2095.891),
                radius=5000.0,
            ),
            Strongpoint(
                id="PAPER MILL",
                name="Paper Mill",
                center=(69319.79, 39032.61, -2095.891),
                radius=3000.0,
            ),
        ),
    ),
)

SECTORS_HILL400_SMALL = Sector.skirmish_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoint=Strongpoint(
        id="HILL 400",
        name="Hill 400",
        center=(0.0, 1015.0, -519.0),
        radius=8000.0,
    ),
)

SECTORS_HURTGENFOREST_LARGE = Sector.large_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoints=(
        (
            Strongpoint(
                id="MAUSBACH APPROACH",
                name="The Masbauch Approach",
                center=(-74423.0, -46733.0, 4336.0),
                radius=4625.0,
            ),
            Strongpoint(
                id="RESERVE STATION",
                name="Reserve Station",
                center=(-78776.0, 2238.0, 3895.0),
                radius=4500.0,
            ),
            Strongpoint(
                id="LUMBER YARD",
                name="Lumber Yard",
                center=(-77356.0, 36029.0, 4122.0),
                radius=4000.0,
            ),
        ),
        (
            Strongpoint(
                id="WEHEBACH OVERLOOK",
                name="Wehebach Overlook",
                center=(-38278.0, -34416.0, 6683.0),
                radius=5031.25,
            ),
            Strongpoint(
                id="KALL TRAIL",
                name="Kall Trail",
                center=(-35755.0, 2459.0, 4007.0),
                radius=6000.0,
            ),
            Strongpoint(
                id="THE RUIN",
                name="The Ruin",
                center=(-42793.0, 26141.0, 3879.0),
                radius=4400.0,
            ),
        ),
        (
            Strongpoint(
                id="NORTH PASS",
                name="North Pass",
                center=(6540.0, -49329.0, 215.0),
                radius=4347.4674749999995,
            ),
            Strongpoint(
                id="THE SCAR",
                name="The Scar",
                center=(-6935.0, 3328.0, 1327.0),
                radius=3015.2502,
            ),
            Strongpoint(
                id="THE SIEGFRIED LINE",
                name="The Siegfried Line",
                center=(-3711.0, 42305.0, 2603.0),
                radius=4500.0,
            ),
        ),
        (
            Strongpoint(
                id="HILL 15",
                name="Hill 15",
                center=(45628.0, -34330.0, 4504.0),
                radius=-4500.0,
            ),
            Strongpoint(
                id="JACOB'S BARN",
                name="Jacob's Barn",
                center=(37658.0, 8531.0, 6550.0),
                radius=3500.0,
            ),
            Strongpoint(
                id="SALIENT 42",
                name="Salient 42",
                center=(40632.0, 50244.0, 6895.0),
                radius=3250.0,
            ),
        ),
        (
            Strongpoint(
                id="GROSSHAU APPROACH",
                name="Grosshau Approach",
                center=(73663.0, -38895.0, 5297.0),
                radius=3750.0,
            ),
            Strongpoint(
                id="HURTGEN APPROACH",
                name="Hürtgen Approach",
                center=(67776.0, 6558.0, 6600.0),
                radius=3500.0,
            ),
            Strongpoint(
                id="LOGGING CAMP",
                name="Logging Camp",
                center=(64477.0, 51502.0, 6495.0),
                radius=3750.0,
            ),
        ),
    ),
)

SECTORS_KHARKOV_LARGE = Sector.large_layout(
    orientation=Orientation.VERTICAL,
    strongpoints=(
        (
            Strongpoint(
                id="MARSH TOWN",
                name="Marsh Town",
                center=(-36517.52, -70661.75, -2300.2422),
                radius=3750.0,
            ),
            Strongpoint(
                id="SOVIET VANTAGE POINT",
                name="Soviet Vantage Point",
                center=(8032.91, -70714.63, 402.14062),
                radius=3750.0,
            ),
            Strongpoint(
                id="GERMAN FUEL DUMP",
                name="German Fuel Dump",
                center=(41168.312, -70231.15, 3192.4492),
                radius=3750.0,
            ),
        ),
        (
            Strongpoint(
                id="BITTER SPRING",
                name="Bitter Spring",
                center=(-37433.285, -38891.406, -2293.7441),
                radius=8000.0,
            ),
            Strongpoint(
                id="LUMBER WORKS",
                name="Lumber Works",
                center=(7916.1367, -39814.156, 279.73047),
                radius=3750.0,
            ),
            Strongpoint(
                id="WINDMILL HILLSIDE",
                name="Windmill Hillside",
                center=(46877.23, -41370.87, 2556.1875),
                radius=3750.0,
            ),
        ),
        (
            Strongpoint(
                id="WATER MILL",
                name="Water Mill",
                center=(-36761.05, -3563.8867, -2120.2441),
                radius=5000.0,
            ),
            Strongpoint(
                id="ST MARY",
                name="St Mary",
                center=(6074.9873, -633.23, 911.6289),
                radius=6000.0,
            ),
            Strongpoint(
                id="DISTILLERY",
                name="Distillery",
                center=(44449.215, -4542.487, 2724.1992),
                radius=3750.0,
            ),
        ),
        (
            Strongpoint(
                id="RIVER CROSSING",
                name="River Crossing",
                center=(-27116.355, 40003.023, -890.95703),
                radius=3750.0,
            ),
            Strongpoint(
                id="BELGOROD OUTSKIRTS",
                name="Belgorod Outskirts",
                center=(8105.9688, 38673.008, 221.38281),
                radius=9000.0,
            ),
            Strongpoint(
                id="LUMBERYARD",
                name="Lumberyard",
                center=(46774.79, 37490.91, 2052.8438),
                radius=3750.0,
            ),
        ),
        (
            Strongpoint(
                id="WEHRMACHT OUTLOOK",
                name="Wehrmacht Overlook",
                center=(-37313.91, 72972.37, -661.0508),
                radius=3750.0,
            ),
            Strongpoint(
                id="HAY STORAGE",
                name="Hay Storage",
                center=(4240.6523, 71736.38, -1926.957),
                radius=3750.0,
            ),
            Strongpoint(
                id="OVERPASS",
                name="Overpass",
                center=(41180.39, 70416.95, -41.4375),
                radius=3750.0,
            ),
        ),
    ),
)

SECTORS_KURSK_LARGE = Sector.large_layout(
    orientation=Orientation.VERTICAL,
    strongpoints=(
        (
            Strongpoint(
                id="ARTILLERY POSITION",
                name="Artillery Position",
                center=(-35117.0, -68921.0, 9323.0),
                radius=6000.0,
            ),
            Strongpoint(
                id="GRUSHKI",
                name="Grushki",
                center=(7070.0, -68141.0, 7093.0),
                radius=4960.5308,
            ),
            Strongpoint(
                id="GRUSHKI FLANK",
                name="Grushki Flank",
                center=(47151.0, -67169.0, 5786.0),
                radius=4500.0,
            ),
        ),
        (
            Strongpoint(
                id="PANZER'S END",
                name="Panzer's End",
                center=(-35117.0, -31958.0, 8935.0),
                radius=6000.0,
            ),
            Strongpoint(
                id="DEFENCE IN DEPTH",
                name="Defence In Depth",
                center=(1604.0, -34906.0, 7647.0),
                radius=7022.2216,
            ),
            Strongpoint(
                id="LISTENING POST",
                name="Listening Post",
                center=(40413.0, -36000.0, 5889.0),
                radius=7673.426,
            ),
        ),
        (
            Strongpoint(
                id="THE WINDMILLS",
                name="The Windmills",
                center=(-26712.39, -4842.251, 9948.998),
                radius=6000.0,
            ),
            Strongpoint(
                id="YAMKI",
                name="Yamki",
                center=(9609.0, 3974.0, 8754.0),
                radius=6973.061,
            ),
            Strongpoint(
                id="OLEG'S HOUSE",
                name="Oleg's House",
                center=(39754.0, 7774.0, 6623.0),
                radius=4500.0,
            ),
        ),
        (
            Strongpoint(
                id="RUDNO",
                name="Rudno",
                center=(-27089.0, 40069.0, 9949.0),
                radius=6000.0,
            ),
            Strongpoint(
                id="DESTROYED BATTERY",
                name="Destroyed Battery",
                center=(-990.0, 39981.0, 10190.0),
                radius=4500.0,
            ),
            Strongpoint(
                id="THE MUDDY CHURN",
                name="The Muddy Churn",
                center=(41089.0, 42772.0, 7983.0),
                radius=4500.0,
            ),
        ),
        (
            Strongpoint(
                id="ROAD TO KURSK",
                name="Road To Kursk",
                center=(-31287.0, 68120.0, 9949.0),
                radius=4500.0,
            ),
            Strongpoint(
                id="AMMO DUMP",
                name="Ammo Dump",
                center=(-1729.0, 66294.0, 9632.0),
                radius=5446.865,
            ),
            Strongpoint(
                id="EASTERN POSITION",
                name="Eastern Position",
                center=(36100.0, 65758.0, 8227.0),
                radius=6000.0,
            ),
        ),
    ),
)

SECTORS_MORTAIN_LARGE = Sector.large_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoints=(
        (
            Strongpoint(
                id="HOTEL DE LA POSTE",
                name="Hotel De La Poste",
                center=(-71664.03, -47217.445, -480.30115),
                radius=5000.0,
            ),
            Strongpoint(
                id="FORWARD BATTERY",
                name="Forward Battery",
                center=(-67949.4, 6438.873, -978.4287),
                radius=6500.0,
            ),
            Strongpoint(
                id="SOUTHERN APPROACH",
                name="Southern Approach",
                center=(-70344.09, 46402.33, -5391.659),
                radius=7500.0,
            ),
        ),
        (
            Strongpoint(
                id="MORTAIN OUTSKIRTS",
                name="Mortain Outskirts",
                center=(-49136.977, -39819.566, 1842.5009),
                radius=6000.0,
            ),
            Strongpoint(
                id="FORWARD MEDICAL AID STATION",
                name="Forward Medical Aid Station",
                center=(-35275.574, -2194.1567, 2411.5898),
                radius=7000.0,
            ),
            Strongpoint(
                id="MORTAIN APPROACH",
                name="Mortain Approach",
                center=(-42775.5, 33050.027, -1580.7439),
                radius=7000.0,
            ),
        ),
        (
            Strongpoint(
                id="HILL 314",
                name="Hill 314",
                center=(-2425.1055, -38259.5, 5891.1714),
                radius=7000.0,
            ),
            Strongpoint(
                id="LA PETITE CHAPELLE SAINT-MICHEL",
                name="La Petite Chapelle Saint-Michel",
                center=(1725.2772, 5918.17, 5670.377),
                radius=5000.0,
            ),
            Strongpoint(
                id="U.S. SOUTHERN ROADBLOCK",
                name="U.S. Southern Roadblock",
                center=(-11254.05, 49076.438, -3064.87),
                radius=7000.0,
            ),
        ),
        (
            Strongpoint(
                id="DESTROYED GERMAN CONVOY",
                name="Destroyed German Convoy",
                center=(35469.836, -42255.99, 6050.5566),
                radius=8000.0,
            ),
            Strongpoint(
                id="GERMAN RECON CAMP",
                name="German Recon Camp",
                center=(40439.145, -2510.7285, 4398.437),
                radius=6000.0,
            ),
            Strongpoint(
                id="LES AUBRILS FARM",
                name="Les Aubrils Farm",
                center=(48018.547, 26619.574, 1071.811),
                radius=6000.0,
            ),
        ),
        (
            Strongpoint(
                id="ABANDONED GERMAN CHECKPOINT",
                name="Abandoned German Checkpoint",
                center=(68651.26, -40271.47, 6068.428),
                radius=6500.0,
            ),
            Strongpoint(
                id="GERMAN DEFENSIVE CAMP",
                name="German Defensive Camp",
                center=(68294.46, 1986.8845, 3941.4448),
                radius=7000.0,
            ),
            Strongpoint(
                id="LE FERME DU DESCHAMPS",
                name="Le Ferme Du Deschamps",
                center=(71327.67, 36841.695, 1896.9764),
                radius=7000.0,
            ),
        ),
    ),
)

SECTORS_MORTAIN_SMALL = Sector.skirmish_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoint=Strongpoint(
        id="LA PETITE CHAPELLE SAINT-MICHEL",
        name="La Petite Chapelle Saint-Michel",
        center=(1000.0, 5500.0, -1000.0),
        radius=6000.0,
    ),
)

SECTORS_OMAHABEACH_LARGE = Sector.large_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoints=(
        (
            Strongpoint(
                id="BEAUMONT ROAD",
                name="Beaumont Road",
                center=(-66508.0, -34528.0, 1461.6543),
                radius=5000.0,
            ),
            Strongpoint(
                id="CROSSROADS",
                name="Crossroads",
                center=(-63975.723, 2684.23, 1607.7931),
                radius=3713.8135,
            ),
            Strongpoint(
                id="LES ISLES",
                name="Les Isles",
                center=(-65785.0, 33673.0, 1949.5156),
                radius=5000.0,
            ),
        ),
        (
            Strongpoint(
                id="REAR BATTERY",
                name="Rear Battery",
                center=(-40364.508, -47019.88, 1471.3027),
                radius=5000.0,
            ),
            Strongpoint(
                id="CHURCH ROAD",
                name="Church Road",
                center=(-36692.0, -9308.0, 1471.3047),
                radius=5000.0,
            ),
            Strongpoint(
                id="THE ORCHARDS",
                name="The Orchards",
                center=(-44319.355, 27163.912, 1705.2588),
                radius=4000.0,
            ),
        ),
        (
            Strongpoint(
                id="WEST VIERVILLE",
                name="West Vierville",
                center=(4665.0, -40540.0, 1262.0),
                radius=5000.0,
            ),
            Strongpoint(
                id="VIERVILLE SUR MER",
                name="Vierville Sur Mer",
                center=(-2661.8896, -2895.0942, 889.7754),
                radius=5000.0,
            ),
            Strongpoint(
                id="ARTILLERY BATTERY",
                name="Artillery Battery",
                center=(2342.277, 31510.633, 1730.7812),
                radius=5000.0,
            ),
        ),
        (
            Strongpoint(
                id="WN73",
                name="WN73",
                center=(54259.0, -44498.0, 164.8125),
                radius=5000.0,
            ),
            Strongpoint(
                id="WN71",
                name="WN71",
                center=(55132.387, -5791.973, 1015.4961),
                radius=3750.0,
            ),
            Strongpoint(
                id="WN70",
                name="WN70",
                center=(46516.0, 30340.0, 1368.2734),
                radius=5000.0,
            ),
        ),
        (
            Strongpoint(
                id="DOG GREEN",
                name="Dog Green",
                center=(67602.0, -31262.0, -3134.6387),
                radius=6250.0,
            ),
            Strongpoint(
                id="THE DRAW",
                name="The Draw",
                center=(71322.0, -7432.0, -2748.504),
                radius=3750.0,
            ),
            Strongpoint(
                id="DOG WHITE",
                name="Dog White",
                center=(71817.0, 30284.0, -3019.504),
                radius=5000.0,
            ),
        ),
    ),
)

SECTORS_PURPLEHEARTLANE_LARGE = Sector.large_layout(
    orientation=Orientation.VERTICAL,
    strongpoints=(
        (
            Strongpoint(
                id="BLOODY BEND",
                name="Bloody Bend",
                center=(-53699.133, -68803.984, 6831.375),
                radius=2750.0,
            ),
            Strongpoint(
                id="DEAD MAN'S CORNER",
                name="Dead Man's Corner",
                center=(740.8672, -65433.984, 6831.375),
                radius=4000.0,
            ),
            Strongpoint(
                id="FORWARD BATTERY",
                name="Forward Battery",
                center=(33330.867, -66643.984, 6831.375),
                radius=4000.0,
            ),
        ),
        (
            Strongpoint(
                id="JOURDAN CANAL",
                name="Jourdan Canal",
                center=(-41489.133, -38108.99, 6831.375),
                radius=2750.0,
            ),
            Strongpoint(
                id="DOUVE BRIDGE",
                name="Douve Bridge",
                center=(-1434.0474, -26826.268, 7010.586),
                radius=4250.0,
            ),
            Strongpoint(
                id="DOUVE RIVER BATTERY",
                name="Douve River Battery",
                center=(33572.38, -36601.72, 6840.3447),
                radius=3500.0,
            ),
        ),
        (
            Strongpoint(
                id="GROULT PILLBOX",
                name="Groult Pillbox",
                center=(-37607.4, -5672.991, 6730.6123),
                radius=5500.0,
            ),
            Strongpoint(
                id="CARENTAN CAUSEWAY",
                name="Carentan Causeway",
                center=(787.74744, 1346.289, 6969.521),
                radius=3500.0,
            ),
            Strongpoint(
                id="FLAK POSITION",
                name="Flak Position",
                center=(45592.906, -4116.6772, 6732.951),
                radius=-4750.0,
            ),
        ),
        (
            Strongpoint(
                id="MADELEINE FARM",
                name="Madeleine Farm",
                center=(-33264.676, 30204.594, 7391.552),
                radius=3250.0,
            ),
            Strongpoint(
                id="MADELEINE BRIDGE",
                name="Madeleine Bridge",
                center=(1928.2188, 39878.098, 6973.26),
                radius=3000.0,
            ),
            Strongpoint(
                id="AID STATION",
                name="Aid Station",
                center=(47043.207, 32172.8, 6753.122),
                radius=3250.0,
            ),
        ),
        (
            Strongpoint(
                id="INGOUF CROSSROADS",
                name="Ingouf Crossroads",
                center=(-36344.676, 66489.59, 7391.552),
                radius=3250.0,
            ),
            Strongpoint(
                id="ROAD TO CARENTAN",
                name="Road To Carentan",
                center=(2953.2188, 63908.098, 6973.26),
                radius=3000.0,
            ),
            Strongpoint(
                id="CABBAGE PATCH",
                name="Cabbage Patch",
                center=(46253.22, 62363.098, 6973.26),
                radius=2500.0,
            ),
        ),
    ),
)

SECTORS_PURPLEHEARTLANE_SMALL = Sector.skirmish_layout(
    orientation=Orientation.VERTICAL,
    strongpoint=Strongpoint(
        id="CARENTAN CAUSEWAY",
        name="Carentan Causeway",
        center=(-960.0, 285.0, 46.0),
        radius=8000.0,
    ),
)

SECTORS_REMAGEN_LARGE = Sector.large_layout(
    orientation=Orientation.VERTICAL,
    strongpoints=(
        (
            Strongpoint(
                id="ALTE LIEBE BARSCH",
                name="Alte Liebe Barsch",
                center=(-41114.0, -69583.0, 6515.0),
                radius=4000.0,
            ),
            Strongpoint(
                id="BEWALDET KREUZUNG",
                name="Bewaldet Kreuzung",
                center=(-891.0, -69550.0, 12708.0),
                radius=4000.0,
            ),
            Strongpoint(
                id="DAN RADART 512",
                name="Dan Radart 512",
                center=(41625.0, -69063.0, 16150.0),
                radius=4000.0,
            ),
        ),
        (
            Strongpoint(
                id="ERPEL",
                name="Erpel",
                center=(-39275.0, -40853.0, 1774.0),
                radius=4000.0,
            ),
            Strongpoint(
                id="ERPELER LEY",
                name="Erpeler Ley",
                center=(9697.0, -42679.0, 13960.0),
                radius=4000.0,
            ),
            Strongpoint(
                id="KASBACH OUTLOOK",
                name="Kasbach Outlook",
                center=(38436.418, -41098.23, 9033.0),
                radius=4000.0,
            ),
        ),
        (
            Strongpoint(
                id="ST. SEVERIN CHAPEL",
                name="St Severin Chapel",
                center=(-39275.0, -12967.0, 766.0),
                radius=4000.0,
            ),
            Strongpoint(
                id="LUDENDORFF BRIDGE",
                name="Ludendorff Bridge",
                center=(3032.2412, 7.0210953, 1261.005),
                radius=8000.0,
            ),
            Strongpoint(
                id="BAUERNHOF AM RHEIN",
                name="Bauernhof Am Rhein",
                center=(38817.02, 15613.944, 104.0),
                radius=4000.0,
            ),
        ),
        (
            Strongpoint(
                id="REMAGEN",
                name="Remagen",
                center=(-35925.75, 39434.0, -27.363525),
                radius=4000.0,
            ),
            Strongpoint(
                id="MÖBELFABRIK",
                name="Möbelfabrik",
                center=(-1000.0, 40824.0, -35.674072),
                radius=5000.0,
            ),
            Strongpoint(
                id="SCHLIEFFEN AUSWEG",
                name="Schlieffen Ausweg",
                center=(39053.0, 38264.0, 104.0),
                radius=4000.0,
            ),
        ),
        (
            Strongpoint(
                id="WALDBURG",
                name="Waldburg",
                center=(-40954.977, 80279.71, -125.40869),
                radius=4000.0,
            ),
            Strongpoint(
                id="MÜHLENWEG",
                name="Mühlenweg",
                center=(3742.6152, 72094.91, -121.5036),
                radius=4000.0,
            ),
            Strongpoint(
                id="HAGELKREUZ",
                name="Hagelkreuz",
                center=(37607.746, 68933.32, 104.0),
                radius=4000.0,
            ),
        ),
    ),
)

SECTORS_SMOLENSK_LARGE = Sector.large_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoints=(
        (
            Strongpoint(
                id="PANZER LOADING STATION",
                name="Panzer Loading Station",
                center=(-68850.08, -40044.953, 512.03125),
                radius=7000.0,
            ),
            Strongpoint(
                id="TRAM DEPOT",
                name="Tram Depot",
                center=(-67850.08, -5084.953, 512.03125),
                radius=7000.0,
            ),
            Strongpoint(
                id="SMOLENSK OUTSKIRTS",
                name="Smolensk Outskirts",
                center=(-68850.08, 40680.047, 512.03125),
                radius=6500.0,
            ),
        ),
        (
            Strongpoint(
                id="SMOLENSK HAUPTBAHNHOF",
                name="Smolensk Hauptbahnhof",
                center=(-38450.08, -40044.953, 512.03125),
                radius=7000.0,
            ),
            Strongpoint(
                id="LUMBER YARD",
                name="Lumber Yard",
                center=(-36050.08, 8915.047, 512.03125),
                radius=9000.0,
            ),
            Strongpoint(
                id="DNIEPER WEST CROSSING",
                name="Dnieper West Crossing",
                center=(-40450.08, 39680.047, 512.03125),
                radius=7000.0,
            ),
        ),
        (
            Strongpoint(
                id="PYATNITSKII OVERPASS",
                name="Pyatnitskii Overpass",
                center=(1000.0, -38544.953, 512.03125),
                radius=6500.0,
            ),
            Strongpoint(
                id="ZHELYABOVA SQUARE",
                name="Zhelyabova Square",
                center=(1000.0, 0.0, 0.0),
                radius=6500.0,
            ),
            Strongpoint(
                id="84TH BATTALION BRIDGE",
                name="84th Battalion Bridge",
                center=(1000.0, 40680.047, 512.03125),
                radius=6000.0,
            ),
        ),
        (
            Strongpoint(
                id="ZADNEPROVIE DISTRICT",
                name="Zadneprovie District",
                center=(39264.92, -40444.953, 512.03125),
                radius=6500.0,
            ),
            Strongpoint(
                id="MOSKOVSKAYA STREET",
                name="Moskovskaya Street",
                center=(39764.92, -1084.9531, 512.03125),
                radius=6500.0,
            ),
            Strongpoint(
                id="SMOLENSK CITADEL",
                name="Smolensk Citadel",
                center=(39264.92, 40680.047, 512.03125),
                radius=7000.0,
            ),
        ),
        (
            Strongpoint(
                id="RAILYARD STORAGE",
                name="Railyard Storage",
                center=(68709.92, -40044.953, 512.03125),
                radius=7000.0,
            ),
            Strongpoint(
                id="APARTMENT BLOCK",
                name="Apartment Block",
                center=(69209.92, -1084.9531, 512.03125),
                radius=7000.0,
            ),
            Strongpoint(
                id="BOMBARDED RIVERFRONT",
                name="Bombarded Riverfront",
                center=(69209.92, 40080.047, 512.03125),
                radius=7000.0,
            ),
        ),
    ),
)

SECTORS_SMOLENSK_SMALL = Sector.skirmish_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoint=Strongpoint(
        id="ZHELYABOVA SQUARE",
        name="Zhelyabova Square",
        center=(1770.0, 0.0, -1735.0),
        radius=8000.0,
    ),
)

SECTORS_STALINGRAD_LARGE = Sector.large_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoints=(
        (
            Strongpoint(
                id="MAMAYEV APPROACH",
                name="Mamayev Approach",
                center=(-69500.0, -47966.0, 5684.0),
                radius=7000.0,
            ),
            Strongpoint(
                id="NAIL FACTORY",
                name="Nail Factory",
                center=(-71016.0, 11068.0, 7295.0),
                radius=8000.0,
            ),
            Strongpoint(
                id="CITY OVERLOOK",
                name="City Overlook",
                center=(-69346.0, 48417.0, 7445.0),
                radius=8000.0,
            ),
        ),
        (
            Strongpoint(
                id="DOLGIY RAVINE",
                name="Dolgiy Ravine",
                center=(-39681.0, -48845.0, 4095.0),
                radius=7500.0,
            ),
            Strongpoint(
                id="YELLOW HOUSE",
                name="Yellow House",
                center=(-39693.438, -1.544678, 7515.0),
                radius=8000.0,
            ),
            Strongpoint(
                id="KOMSOMOL HQ",
                name="Komsomol HQ",
                center=(-39683.0, 39676.0, 7310.0),
                radius=8000.0,
            ),
        ),
        (
            Strongpoint(
                id="RAILWAY CROSSING",
                name="Railway Crossing",
                center=(7.0, -39673.0, 4505.0),
                radius=8000.0,
            ),
            Strongpoint(
                id="CARRIAGE DEPOT",
                name="Carriage Depot",
                center=(-15.0, 13.0, 4961.0),
                radius=8500.0,
            ),
            Strongpoint(
                id="TRAIN STATION",
                name="Train Station",
                center=(6.0, 39678.0, 4942.0),
                radius=8000.0,
            ),
        ),
        (
            Strongpoint(
                id="HOUSE OF THE WORKERS",
                name="House Of The Workers",
                center=(36591.0, -40602.0, 4355.0),
                radius=8000.0,
            ),
            Strongpoint(
                id="PAVLOV'S HOUSE",
                name="Pavlov's House",
                center=(48586.0, 1452.0, 4035.0),
                radius=8000.0,
            ),
            Strongpoint(
                id="THE BREWERY",
                name="The Brewery",
                center=(39674.0, 41970.0, 4077.0),
                radius=8000.0,
            ),
        ),
        (
            Strongpoint(
                id="L-SHAPED HOUSE",
                name="L-Shaped House",
                center=(68875.0, -35043.0, 4195.0),
                radius=8000.0,
            ),
            Strongpoint(
                id="GRUDININ'S MILL",
                name="Grudinin's Mill",
                center=(70063.0, -32.0, 3965.0),
                radius=8000.0,
            ),
            Strongpoint(
                id="VOLGA BANKS",
                name="Volga Banks",
                center=(70121.0, 43351.0, 3965.0),
                radius=8000.0,
            ),
        ),
    ),
)

SECTORS_STALINGRAD_SMALL = Sector.skirmish_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoint=Strongpoint(
        id="CARRIAGE DEPOT",
        name="Carriage Depot",
        center=(0.0, 0.0, -1388.4307),
        radius=6000.0,
    ),
)

SECTORS_STMARIEDUMONT_LARGE = Sector.large_layout(
    orientation=Orientation.VERTICAL,
    strongpoints=(
        (
            Strongpoint(
                id="WINTERS LANDING",
                name="Winters Landing",
                center=(-39503.258, -78343.03, 809.0),
                radius=5754.7485,
            ),
            Strongpoint(
                id="LE GRAND CHEMIN",
                name="Le Grand Chemin",
                center=(-367.0, -76667.0, 809.0),
                radius=4500.0,
            ),
            Strongpoint(
                id="THE BARN",
                name="The Barn",
                center=(44896.0, -73822.0, -89.0),
                radius=5691.033,
            ),
        ),
        (
            Strongpoint(
                id="BRECOURT BATTERY",
                name="Brecourt Battery",
                center=(-39380.0, -39702.0, 809.0),
                radius=6078.6405,
            ),
            Strongpoint(
                id="CATTLESHEDS",
                name="Cattlesheds",
                center=(2961.319, -41557.402, 809.0),
                radius=5400.8775,
            ),
            Strongpoint(
                id="RUE DE LA GARE",
                name="Rue De La Gare",
                center=(35565.562, -39370.594, 809.0),
                radius=5892.7635,
            ),
        ),
        (
            Strongpoint(
                id="THE DUGOUT",
                name="The Dugout",
                center=(-37170.906, -151.18701, 460.30884),
                radius=5814.819,
            ),
            Strongpoint(
                id="AA NETWORK",
                name="AA Network",
                center=(1716.0, 2530.0, 422.64746),
                radius=6530.8635,
            ),
            Strongpoint(
                id="PIERRE'S FARM",
                name="Pierre's Farm",
                center=(37508.1, 1336.6963, 438.40137),
                radius=5207.283,
            ),
        ),
        (
            Strongpoint(
                id="HUGO'S FARM",
                name="Hugo's Farm",
                center=(-38001.0, 38089.0, 809.0),
                radius=6046.29,
            ),
            Strongpoint(
                id="THE HAMLET",
                name="The Hamlet",
                center=(-2158.7668, 42649.312, 597.02246),
                radius=4500.0,
            ),
            Strongpoint(
                id="STE MARIE DU MONT",
                name="Ste Marie Du Mont",
                center=(47022.125, 50258.56, 1336.7599),
                radius=6000.0,
            ),
        ),
        (
            Strongpoint(
                id="THE CORNER",
                name="The Corner",
                center=(-34620.76, 69152.766, 809.0),
                radius=5105.9565,
            ),
            Strongpoint(
                id="HILL 6",
                name="Hill 6",
                center=(142.14453, 76822.93, 467.88086),
                radius=4500.0,
            ),
            Strongpoint(
                id="THE FIELDS",
                name="The Fields",
                center=(39750.15, 78234.78, 1152.4478),
                radius=4500.0,
            ),
        ),
    ),
)

SECTORS_STMARIEDUMONT_SMALL = Sector.skirmish_layout(
    orientation=Orientation.VERTICAL,
    strongpoint=Strongpoint(
        id="CATTLESHEDS",
        name="Cattlesheds",
        center=(3670.0, -2995.0, 125.0),
        radius=10000.0,
    ),
)

SECTORS_STMEREEGLISE_LARGE = Sector.large_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoints=(
        (
            Strongpoint(
                id="FLAK POSITION",
                name="Flak Position",
                center=(-69311.0, -40772.0, -81.0),
                radius=4000.0,
            ),
            Strongpoint(
                id="VAULAVILLE",
                name="Vaulaville",
                center=(-62223.0, -3146.0, -1163.0),
                radius=2507.38,
            ),
            Strongpoint(
                id="LA PRAIRIE",
                name="La Prairie",
                center=(-67517.0, 35037.0, 1050.0),
                radius=4000.0,
            ),
        ),
        (
            Strongpoint(
                id="ROUTE DU HARAS",
                name="Route Du Haras",
                center=(-40886.0, -37779.0, -688.63086),
                radius=4000.0,
            ),
            Strongpoint(
                id="WESTERN APPROACH",
                name="Western Approach",
                center=(-32652.0, -14761.0, -400.0),
                radius=4000.0,
            ),
            Strongpoint(
                id="RUE DE GAMBOSVILLE",
                name="Rue De Gambosville",
                center=(-34553.0, 41733.0, -699.0),
                radius=4000.0,
            ),
        ),
        (
            Strongpoint(
                id="HOSPICE",
                name="Hospice",
                center=(-1100.0, -46000.0, -400.0),
                radius=4000.0,
            ),
            Strongpoint(
                id="SAINTE-MÈRE-ÉGLISE",
                name="Sainte-Mère-Église",
                center=(5949.0, -7436.0, -718.7539),
                radius=4741.136,
            ),
            Strongpoint(
                id="CHECKPOINT",
                name="Checkpoint",
                center=(467.0, 32490.0, -1330.0),
                radius=4000.0,
            ),
        ),
        (
            Strongpoint(
                id="ARTILLERY BATTERY",
                name="Artillery Battery",
                center=(39652.0, -34374.0, -400.0),
                radius=4000.0,
            ),
            Strongpoint(
                id="THE CEMETERY",
                name="The Cemetery",
                center=(28858.0, 5593.0, -742.64844),
                radius=4000.0,
            ),
            Strongpoint(
                id="MAISON DU CRIQUE",
                name="Maison Du Crique",
                center=(25884.0, 30530.0, -400.0),
                radius=4000.0,
            ),
        ),
        (
            Strongpoint(
                id="LES VIEUX VERGERS",
                name="Les Vieux Vergers",
                center=(70168.0, -28861.0, -743.6719),
                radius=4000.0,
            ),
            Strongpoint(
                id="CROSS ROADS",
                name="Cross Roads",
                center=(72279.0, 1393.0, -676.0),
                radius=4000.0,
            ),
            Strongpoint(
                id="RUISSEAU DE FERME",
                name="Russeau De Ferme",
                center=(72138.0, 38912.0, -1125.0),
                radius=4000.0,
            ),
        ),
    ),
)

SECTORS_STMEREEGLISE_SMALL = Sector.skirmish_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoint=Strongpoint(
        id="SAINTE-MÈRE-ÉGLISE",
        name="Sainte-Mère-Église",
        center=(165.0, -113.0, -76.0),
        radius=8000.0,
    ),
)

SECTORS_TOBRUK_LARGE = Sector.large_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoints=(
        (
            Strongpoint(
                id="GUARD ROOM",
                name="Guard Room",
                center=(-68855.0, -27530.0, -6107.8867),
                radius=7000.0,
            ),
            Strongpoint(
                id="TANK GRAVEYARD",
                name="Tank Graveyard",
                center=(-69405.0, -2075.0, -7493.6714),
                radius=8000.0,
            ),
            Strongpoint(
                id="DIVISION HEADQUARTERS",
                name="Division Headquarters",
                center=(-69835.0, 45005.0, -8821.878),
                radius=7000.0,
            ),
        ),
        (
            Strongpoint(
                id="WEST CREEK",
                name="West Creek",
                center=(-40077.0, -44015.0, -5846.329),
                radius=8000.0,
            ),
            Strongpoint(
                id="ALBERGO RISTORANTE MODERNO",
                name="Albergo Ristorante Moderno",
                center=(-29536.549, 2241.0, -7323.1304),
                radius=7000.0,
            ),
            Strongpoint(
                id="KING SQUARE",
                name="King Square",
                center=(-29485.152, 39744.316, -7213.4697),
                radius=8000.0,
            ),
        ),
        (
            Strongpoint(
                id="DESERT RAT CAVES",
                name="Desert Rat Caves",
                center=(31.221313, -39665.25, -5381.714),
                radius=8000.0,
            ),
            Strongpoint(
                id="CHURCH GROUNDS",
                name="Church Grounds",
                center=(59.92363, 11770.049, -7002.9688),
                radius=7000.0,
            ),
            Strongpoint(
                id="ADMIRALTY HOUSE",
                name="Admiralty House",
                center=(7919.4326, 48901.832, -7326.4785),
                radius=9000.0,
            ),
        ),
        (
            Strongpoint(
                id="ABANDONED AMMO CACHE",
                name="Abandoned Ammo Cache",
                center=(39687.508, -39659.996, -4662.4526),
                radius=8000.0,
            ),
            Strongpoint(
                id="8TH ARMY MEDICAL HOSPITAL",
                name="8th Army Medical Hospital",
                center=(40124.035, -2845.0, -7074.448),
                radius=9000.0,
            ),
            Strongpoint(
                id="SUPPLY DUMP",
                name="Supply Dump",
                center=(39820.547, 43918.36, -7314.533),
                radius=9000.0,
            ),
        ),
        (
            Strongpoint(
                id="ROAD TO SENUSSI MINE",
                name="Road To Senussi Mine",
                center=(69522.8, -40790.0, -4568.7607),
                radius=7000.0,
            ),
            Strongpoint(
                id="MAKESHIFT AID STATION",
                name="Makeshift Aid Station",
                center=(69380.0, 25.0, -6849.7656),
                radius=9000.0,
            ),
            Strongpoint(
                id="CARGO WAREHOUSES",
                name="Cargo Warehouses",
                center=(70047.33, 41171.96, -7616.6694),
                radius=8000.0,
            ),
        ),
    ),
)

SECTORS_TOBRUK_SMALL = Sector.skirmish_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoint=Strongpoint(
        id="CHURCH GROUNDS",
        name="Church Grounds",
        center=(0.0, 7625.0, -844.0),
        radius=6000.0,
    ),
)

SECTORS_UTAHBEACH_LARGE = Sector.large_layout(
    orientation=Orientation.HORIZONTAL,
    strongpoints=(
        (
            Strongpoint(
                id="MAMMUT RADAR",
                name="Mammut Radar",
                center=(-65158.0, -51522.0, -2401.0),
                radius=3000.0,
            ),
            Strongpoint(
                id="FLOODED HOUSE",
                name="Flooded House",
                center=(-66464.0, -2944.0, -2388.0),
                radius=3000.0,
            ),
            Strongpoint(
                id="SAINTE MARIE APPROACH",
                name="Sainte Marie Approach",
                center=(-64837.0, 52705.0, -2157.0),
                radius=3000.0,
            ),
        ),
        (
            Strongpoint(
                id="SUNKEN BRIDGE",
                name="Sunken Bridge",
                center=(-30810.0, -47853.0, -2157.0),
                radius=3000.0,
            ),
            Strongpoint(
                id="LA GRANDE CRIQUE",
                name="La Grande Crique",
                center=(-28986.0, 508.0, -2388.0),
                radius=3294.095,
            ),
            Strongpoint(
                id="DROWNED FIELDS",
                name="Drowned Fields",
                center=(-36400.0, 43928.0, -2157.0),
                radius=3000.0,
            ),
        ),
        (
            Strongpoint(
                id="WN4",
                name="WN4",
                center=(5359.0, -42267.0, -2283.0),
                radius=3742.354,
            ),
            Strongpoint(
                id="THE CHAPEL",
                name="The Chapel",
                center=(10650.0, -7786.0, -2157.0),
                radius=3000.0,
            ),
            Strongpoint(
                id="WN7",
                name="WN7",
                center=(727.0, 50408.0, -2157.0),
                radius=5000.0,
            ),
        ),
        (
            Strongpoint(
                id="AA BATTERY",
                name="AA Battery",
                center=(35101.0, -43589.0, -2389.0),
                radius=3941.9941,
            ),
            Strongpoint(
                id="HILL 5",
                name="Hill 5",
                center=(36131.0, -1838.0, -2157.0),
                radius=3000.0,
            ),
            Strongpoint(
                id="WN5",
                name="WN5",
                center=(48763.0, 44080.0, -2247.0),
                radius=3194.091,
            ),
        ),
        (
            Strongpoint(
                id="TARE GREEN",
                name="Tare Green",
                center=(63845.0, -46581.0, -2284.0),
                radius=3000.0,
            ),
            Strongpoint(
                id="RED ROOF HOUSE",
                name="Red Roof House",
                center=(64923.67, 3144.1865, -2206.6382),
                radius=3250.0,
            ),
            Strongpoint(
                id="UNCLE RED",
                name="Uncle Red",
                center=(66675.0, 45162.0, -2157.0),
                radius=2823.963,
            ),
        ),
    ),
)
