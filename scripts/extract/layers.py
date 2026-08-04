import logging
from collections.abc import Iterator
from pathlib import Path
from typing import NotRequired, TypedDict

from pydantic import BaseModel, model_validator

from hllrcon.data.game_modes import AnyGameMode, GameModeScale, HLLVGameMode
from hllrcon.data.layers import TimeOfDay, Weather
from hllrcon.data.teams import AnyTeam
from scripts import HLLV_METADATA_PATH
from scripts.extract.maps import MapData, get_all_maps, get_map_data
from scripts.extract.utils import inject_code, to_method_name
from scripts.extractlib.loader import set_root_path
from scripts.extractlib.objects.layout_meta_data_asset import LayoutMetaDataAsset
from scripts.extractlib.objects.map_meta_data_asset import MapMetaDataAsset
from scripts.extractlib.objects.scenario_meta_data_asset import ScenarioMetaDataAsset
from scripts.extractlib.structs.vec2 import Vec2

logger = logging.getLogger(__name__)

HLLV_LAYER_OUTPUT_PATH = Path("hllrcon/data/layers.py")
HLLV_LAYER_DIRS: list[Path] = [
    Path("HLLVietnam/Content/_WFL/Maps/CAM_L_1969"),
    Path("HLLVietnam/Content/_WFL/Maps/DAK_L_1967"),
    Path("HLLVietnam/Content/_WFL/Maps/HUE_L_1968"),
    Path("HLLVietnam/Content/_WFL/Maps/QUA_L_1965"),
    Path("HLLVietnam/Content/_WFL/Maps/THA_L_1965"),
    Path("HLLVietnam/Content/_WFL/Maps/VAN_L_1965"),
]
HLLV_LAYER_CONSTRUCTOR_TEMPLATE = """\
    @class_cached_property
    @classmethod
    def {layer.meth_name}(cls) -> "HLLVLayer":
        return cls(
            id={layer.id!r},
            map=HLLVMap.{layer.map.meth_name},
            game_mode=HLLVGameMode.{game_mode},
            time_of_day=TimeOfDay.{layer.time_of_day.name},
            weather=Weather.{layer.weather.name},
            grid=Grid(
                scale={layer.grid.scale},
                offset=({layer.grid.offset.x}, {layer.grid.offset.y}),
                size=(
                    ({layer.grid.size[0].x:.0f}, {layer.grid.size[0].y:.0f}),
                    ({layer.grid.size[1].x:.0f}, {layer.grid.size[1].y:.0f}),
                ),
            ),
            sectors={sectors},
        )"""

_layer_id_no_metadata_warned: set[str] = set()


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


class LayerData(BaseModel):
    meth_name: str = ""
    id: str
    map: MapData
    game_mode: AnyGameMode
    time_of_day: TimeOfDay = TimeOfDay.DAY
    weather: Weather = Weather.CLEAR
    grid: LayerGridData
    attacking_team: AnyTeam | None

    @model_validator(mode="after")
    def set_meth_name(self) -> "LayerData":
        metadata = HLLV_LAYER_METADATA
        meta = metadata.get(self.id)
        if meta is not None:
            self.meth_name = meta.get("meth_name", self.meth_name)
            self.time_of_day = meta.get("time_of_day", self.time_of_day)
            self.weather = meta.get("weather", self.weather)
        elif self.id not in _layer_id_no_metadata_warned:
            logger.warning("No metadata found for layer ID: %s", self.id)
            _layer_id_no_metadata_warned.add(self.id)

        if not self.meth_name:
            self.meth_name = to_method_name(self.id)
        return self

    def to_constructor(self) -> str:
        template = HLLV_LAYER_CONSTRUCTOR_TEMPLATE

        if self.game_mode.id == HLLVGameMode.CONQUEST.id:
            sectors_meth_id = (
                f"SECTORS_{self.map.meth_name}_{self.game_mode.id}".upper()
            )
        elif self.game_mode.scale == GameModeScale.LARGE:
            sectors_meth_id = f"SECTORS_{self.map.meth_name}_WARFARE"
        else:
            sectors_meth_id = f"SECTORS_{self.map.meth_name}_SKIRMISH"

        return template.format(
            layer=self,
            game_mode=self.game_mode.id.upper(),
            sectors=sectors_meth_id,
        )


def get_all_layers() -> Iterator[tuple[ScenarioMetaDataAsset, MapMetaDataAsset]]:
    for map_meta in get_all_maps():
        for scenario_meta in map_meta.properties.get_scenarios():
            yield scenario_meta, map_meta


def get_layer_data(
    scenario_meta: ScenarioMetaDataAsset,
    map_meta: MapMetaDataAsset,
) -> LayerData | None:
    props = scenario_meta.properties
    game_mode_meta = props.get_game_mode()
    layout_meta = game_mode_meta.properties.get_layout()
    try:
        game_mode = HLLVGameMode.by_id(game_mode_meta.properties.get_game_mode_id())
    except ValueError:
        logger.warning(
            "Skipping layer with unknown game mode: %s (scenario: %s, map: %s)",
            game_mode_meta.properties.get_game_mode_id(),
            scenario_meta.get_name(),
            map_meta.get_name(),
        )
        return None

    return LayerData(
        id=props.get_layer_id(map_meta),
        map=get_map_data(map_meta),
        game_mode=game_mode,
        grid=LayerGridData.from_layout_meta(layout_meta),
        attacking_team=game_mode_meta.properties.attacking_team.to_hllv_team(),
    )


def get_all_layer_data() -> Iterator[LayerData]:
    for scenario_meta, map_meta in get_all_layers():
        layer_data = get_layer_data(scenario_meta, map_meta)
        if layer_data is not None:
            yield layer_data


def main() -> None:
    set_root_path(HLLV_METADATA_PATH)

    layers = list(get_all_layer_data())
    layer_constructors = [layer.to_constructor() for layer in layers]

    inject_code(
        HLLV_LAYER_OUTPUT_PATH,
        "hllv layers",
        "\n\n".join(layer_constructors),
    )


class LayerMetaData(TypedDict):
    meth_name: NotRequired[str]
    time_of_day: TimeOfDay
    weather: Weather


HLLV_LAYER_METADATA: dict[str, LayerMetaData] = {
    "WDEV_A_Warfare_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_A_OffensiveNVA_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_A_OffensiveUS_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_A_Domination_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_B_OffensiveNVA_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_B_OffensiveUS_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_B_Domination_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_B_Conquest_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_C_Warfare_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_C_OffensiveNVA_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_C_OffensiveUS_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_C_Domination_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_C_Conquest_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_D_Warfare_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_D_OffensiveNVA_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_D_OffensiveUS_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_D_Domination_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_D_Conquest_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_E_Warfare_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_E_OffensiveNVA_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_E_OffensiveUS_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_E_Domination_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_E_Conquest_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_B_Warfare_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_F_Warfare_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_F_OffensiveNVA_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_F_OffensiveUS_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_F_Domination_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
    "WDEV_F_Conquest_Day": {
        "time_of_day": TimeOfDay.DAY,
        "weather": Weather.CLEAR,
    },
}

if __name__ == "__main__":
    main()
