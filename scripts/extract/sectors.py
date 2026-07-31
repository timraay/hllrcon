import logging
from collections.abc import Iterator
from pathlib import Path
from typing import cast

from pydantic import BaseModel, model_validator

from hllrcon.data.game_modes import AnyGameMode, HLLVGameMode
from hllrcon.data.maps import Orientation
from scripts import HLLV_METADATA_PATH
from scripts.extract.layers import HLLV_LAYER_OUTPUT_PATH
from scripts.extract.maps import HLLV_MAP_DIRS, MapData, get_all_maps, get_map_data
from scripts.extract.utils import inject_code
from scripts.extractlib.loader import Object, local_to_abs_path, set_root_path
from scripts.extractlib.objects.conquest_objectives_phase1 import (
    ConquestObjectivesPhase1,
)
from scripts.extractlib.objects.layout_meta_data_asset import LayoutMetaDataAsset
from scripts.extractlib.objects.level import Level
from scripts.extractlib.objects.map_meta_data_asset import MapMetaDataAsset
from scripts.extractlib.objects.sphere_component import SphereComponent
from scripts.extractlib.objects.sphere_sector_capture_booster import (
    SphereSectorCaptureBooster,
)
from scripts.extractlib.objects.world import World
from scripts.extractlib.structs.vec2 import Vec2
from scripts.extractlib.structs.vec3 import Vec3
from scripts.extractlib.utils import find_objects_in_dir

logger = logging.getLogger(__name__)

HLLV_SECTOR_OUTPUT_PATH = Path("hllrcon/data/sectors.py")
HLLV_SECTOR_CONSTRUCTOR_TEMPLATE = """\
{sector.meth_name} = Sector.{game_mode_name}_layout(
    orientation=Orientation.{orientation.name},
    strongpoints=(
{strongpoints}
    ),
)"""
HLLV_SECTOR_ROW_CONSTRUCTOR_TEMPLATE = """\
        (
{strongpoints}
        ),"""
HLLV_SECTOR_STRONGPOINT_CONSTRUCTOR_TEMPLATE = """\
            Strongpoint(
                id={strongpoint.name!r},
                name={strongpoint.name!r},
                center=({strongpoint.position.x}, {strongpoint.position.y}, {strongpoint.position.z}),
                radius={strongpoint.radius},
            ),"""  # noqa: E501


class LayerGridData(BaseModel):
    scale: float
    offset: Vec2
    size: tuple[Vec2, Vec2]

    @classmethod
    def from_layout_meta(cls, layout_meta: LayoutMetaDataAsset) -> "LayerGridData":
        props = layout_meta.properties
        if props.sector_height != props.sector_width:
            msg = (
                f"Layout {layout_meta.get_name()} has non-square sectors: "
                f"width={props.sector_width}, height={props.sector_height}"
            )
            raise ValueError(msg)

        return cls(
            scale=props.sector_height / 2,
            offset=props.map_centre,
            size=(
                Vec2(x=-props.map_width, y=-props.map_height),
                Vec2(x=props.map_width - 1, y=props.map_height - 1),
            ),
        )


class SectorStrongpointData(BaseModel):
    position: Vec3
    radius: float
    name: str

    def get_grid_position(self, grid: LayerGridData | LayoutMetaDataAsset) -> Vec2:
        if isinstance(grid, LayoutMetaDataAsset):
            grid = LayerGridData.from_layout_meta(grid)

        scale = grid.scale * 2

        return Vec2(
            x=round((self.position.x - grid.offset.x) / scale),
            y=round((self.position.y - grid.offset.y) / scale),
        )

    def to_constructor(self) -> str:
        return HLLV_SECTOR_STRONGPOINT_CONSTRUCTOR_TEMPLATE.format(
            strongpoint=self,
        )


class SectorData(BaseModel):
    meth_name: str = ""
    map: MapData
    game_mode: AnyGameMode
    orientation: Orientation
    strongpoints: list[SectorStrongpointData]
    grid: LayerGridData

    @model_validator(mode="after")
    def set_meth_name(self) -> "SectorData":
        if not self.meth_name:
            self.meth_name = f"SECTORS_{self.map.meth_name}_{self.game_mode.id}".upper()
        return self

    @model_validator(mode="after")
    def sort_strongpoints(self) -> "SectorData":
        sort_strongpoints(self.strongpoints, self.grid, self.orientation)
        return self

    def to_constructor(self) -> str:
        template = HLLV_SECTOR_CONSTRUCTOR_TEMPLATE

        if self.game_mode.id == HLLVGameMode.CONQUEST.id:
            expected_strongpoints_count = 5
            grouped_strongpoints = [
                self.strongpoints[0:1],
                self.strongpoints[1:4],
                self.strongpoints[4:5],
            ]
        else:
            expected_strongpoints_count = 15
            grouped_strongpoints = [
                self.strongpoints[i : i + 3]
                for i in range(0, len(self.strongpoints), 3)
            ]

        if len(self.strongpoints) != expected_strongpoints_count:
            logger.warning(
                "Unexpected number of strongpoints for sector %s: %d (expected %d)",
                self.meth_name,
                len(self.strongpoints),
                expected_strongpoints_count,
            )

        strongpoints = "\n".join(
            [
                HLLV_SECTOR_ROW_CONSTRUCTOR_TEMPLATE.format(
                    strongpoints="\n".join(
                        [
                            strongpoint.to_constructor()
                            for strongpoint in strongpoint_group
                        ],
                    ),
                )
                for strongpoint_group in grouped_strongpoints
            ],
        )

        return template.format(
            sector=self,
            game_mode_name=self.game_mode.id.lower(),
            strongpoints=strongpoints,
            orientation=self.map.allies_direction.to_orientation(),
        )


def get_all_warfare_gp_levels() -> Iterator[Level | None]:
    for map_dir in HLLV_MAP_DIRS:
        for world, _ in find_objects_in_dir(
            local_to_abs_path(map_dir / "GP", add_ext=False),
            lambda obj: obj.type == "World",
            obj_type=World,
            glob_pattern="*GP_CaptureBoosters.json",
        ):
            yield world.persistent_level.get(Level)
            break
        else:
            logger.warning(
                "No capture boosters level found for map: %s",
                map_dir.name or map_dir,
            )
            yield None


def get_all_conquest_gp_levels() -> Iterator[Level | None]:
    for map_dir in HLLV_MAP_DIRS:
        for world, _ in find_objects_in_dir(
            local_to_abs_path(map_dir / "GP", add_ext=False),
            lambda obj: obj.type == "World",
            obj_type=World,
            glob_pattern="*GP_Conquest.json",
        ):
            yield world.persistent_level.get(Level)
            break
        else:
            logger.warning(
                "No conquest level found for map: %s",
                map_dir.name or map_dir,
            )
            yield None


def get_sphere_components_from_warfare_level(level: Level) -> Iterator[SphereComponent]:
    for actor_ref in level.actors:
        if actor_ref and actor_ref.get(Object).type == "SphereSectorCaptureBooster":
            capture_booster = cast(
                "SphereSectorCaptureBooster",
                actor_ref.get(SphereSectorCaptureBooster),
            )
            sphere = capture_booster.properties.trigger_shape.get(SphereComponent)
            yield sphere


def get_sphere_components_from_conquest_level(
    level: Level,
) -> Iterator[SphereComponent]:
    for actor_ref in level.actors:
        if (
            actor_ref
            and actor_ref.get(Object).type == "BP_Conquest_Objectives_Phase1_C"
        ):
            objectives = cast(
                "ConquestObjectivesPhase1",
                actor_ref.get(ConquestObjectivesPhase1),
            )
            for objective in objectives.properties.get_objectives():
                sphere = objective.properties.get_hard_capture_point_shape()
                yield sphere


def sort_strongpoints(
    strongpoints: list[SectorStrongpointData],
    grid: LayerGridData | LayoutMetaDataAsset,
    orientation: Orientation = Orientation.VERTICAL,
) -> None:
    if isinstance(grid, LayoutMetaDataAsset):
        grid = LayerGridData.from_layout_meta(grid)

    scale = grid.scale * 2

    # Sort from left to right, top to bottom (y first, then x)
    if orientation == Orientation.HORIZONTAL:
        strongpoints.sort(
            key=lambda s: (
                round(s.position.x / scale),
                round(s.position.y / scale),
            ),
        )
    else:
        strongpoints.sort(
            key=lambda s: (
                round(s.position.y / scale),
                round(s.position.x / scale),
            ),
        )


def get_sector_strongpoint_data(
    level: Level | None,
    map_meta: MapMetaDataAsset,
    game_mode: HLLVGameMode,
) -> list[SectorStrongpointData]:
    orientation = map_meta.properties.get_direction().to_orientation()
    scenario = map_meta.properties.get_scenario(game_mode)
    game_mode_meta = scenario.properties.get_game_mode()
    layout_meta = game_mode_meta.properties.get_layout()
    grid = LayerGridData.from_layout_meta(layout_meta)

    default_strongpoints = [
        SectorStrongpointData(
            position=Vec3(
                x=layout_meta.properties.sector_width
                * (x if orientation == Orientation.HORIZONTAL else y),
                y=layout_meta.properties.sector_height
                * (y if orientation == Orientation.HORIZONTAL else x),
                z=0,
            ),
            radius=1.0,
            name="",
        )
        for x in range(-2, 3)
        for y in range(-1, 2)
    ]
    sort_strongpoints(default_strongpoints, layout_meta)

    if level is None:
        strongpoints = default_strongpoints
    elif game_mode == HLLVGameMode.WARFARE:
        strongpoints = [
            SectorStrongpointData(
                position=sphere.properties.relative_location,
                radius=sphere.properties.sphere_radius,
                name="",
            )
            for sphere in get_sphere_components_from_warfare_level(level)
        ]
    elif game_mode == HLLVGameMode.CONQUEST:
        strongpoints = [
            SectorStrongpointData(
                position=sphere.properties.relative_location,
                radius=sphere.properties.sphere_radius,
                name="",
            )
            for sphere in get_sphere_components_from_conquest_level(level)
        ]
    else:
        msg = f"Unsupported game mode for sector strongpoint extraction: {game_mode.id}"
        raise ValueError(msg)

    # Sort from left to right, top to bottom (y first, then x)
    sort_strongpoints(strongpoints, layout_meta)

    sector_names = [
        (sector.name, strongpoint.get_grid_position(grid))
        for sector, strongpoint in zip(
            game_mode_meta.properties.sector_definitions,
            default_strongpoints,
            strict=True,
        )
    ]

    for strongpoint in strongpoints:
        strongpoint_grid_pos = strongpoint.get_grid_position(grid)
        for name, grid_pos in sector_names:
            if strongpoint_grid_pos == grid_pos:
                strongpoint.name = str(name)
                break
        else:
            msg = f"Strongpoint at {strongpoint.position} has no matching sector name"
            raise ValueError(msg)

    return strongpoints


def get_sector_data(
    level: Level | None,
    map_meta: MapMetaDataAsset,
    game_mode: HLLVGameMode,
) -> SectorData:
    orientation = map_meta.properties.get_direction().to_orientation()
    layout_meta = (
        map_meta.properties.get_scenario(game_mode)
        .properties.get_game_mode()
        .properties.get_layout()
    )

    strongpoints = get_sector_strongpoint_data(level, map_meta, game_mode)
    return SectorData(
        map=get_map_data(map_meta),
        game_mode=game_mode,
        orientation=orientation,
        strongpoints=strongpoints,
        grid=LayerGridData.from_layout_meta(layout_meta),
    )


def get_all_sector_data() -> Iterator[SectorData]:
    for level, map_meta in zip(
        get_all_warfare_gp_levels(),
        get_all_maps(),
        strict=True,
    ):
        yield get_sector_data(level, map_meta, game_mode=HLLVGameMode.WARFARE)

    for level, map_meta in zip(
        get_all_conquest_gp_levels(),
        get_all_maps(),
        strict=True,
    ):
        yield get_sector_data(level, map_meta, game_mode=HLLVGameMode.CONQUEST)


def main() -> None:
    set_root_path(HLLV_METADATA_PATH)

    sectors = list(get_all_sector_data())
    sector_constructors = [sector.to_constructor() for sector in sectors]

    inject_code(
        HLLV_SECTOR_OUTPUT_PATH,
        "hllv sectors",
        "\n\n".join(sector_constructors),
    )

    inject_code(
        HLLV_LAYER_OUTPUT_PATH,
        "hllv sector imports",
        "\n".join(
            [
                f"    from hllrcon.data.sectors import {sector.meth_name}"
                for sector in sectors
            ],
        ),
    )


if __name__ == "__main__":
    main()
