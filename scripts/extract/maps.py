import logging
from collections.abc import Iterator
from pathlib import Path
from typing import NotRequired, TypedDict

from pydantic import BaseModel, model_validator

from hllrcon.data.factions import AnyFaction
from hllrcon.data.maps import CardinalDirection
from scripts import HLLV_METADATA_PATH
from scripts.extract.utils import inject_code, load_meta, save_meta, to_method_name
from scripts.extractlib.loader import local_to_abs_path, set_root_path
from scripts.extractlib.objects.map_meta_data_asset import MapMetaDataAsset
from scripts.extractlib.utils import find_objects_in_dir

logger = logging.getLogger(__name__)

HLLV_MAP_OUTPUT_PATH = Path("hllrcon/data/maps.py")
HLLV_MAP_DIRS: list[Path] = [
    Path("HLLVietnam/Content/_WFL/Maps/CAM_L_1969"),
    Path("HLLVietnam/Content/_WFL/Maps/DAK_L_1967"),
    Path("HLLVietnam/Content/_WFL/Maps/HUE_L_1968"),
    Path("HLLVietnam/Content/_WFL/Maps/QUA_L_1965"),
    Path("HLLVietnam/Content/_WFL/Maps/THA_L_1965"),
    Path("HLLVietnam/Content/_WFL/Maps/VAN_L_1965"),
]
HLLV_MAP_CONSTRUCTOR_TEMPLATE = """\
    @class_cached_property
    @classmethod
    def {map.meth_name}(cls) -> "HLLVMap":
        return cls(
            id={map.id!r},
            name={map.name!r},
            tag={map.tag!r},
            year={map.year},
            pretty_name={map.pretty_name!r},
            short_name={map.short_name!r},
            allies=HLLVFaction.{map.allies.short_name},
            axis=HLLVFaction.{map.axis.short_name},
            allies_direction=CardinalDirection.{map.allies_direction.name},
        )"""

_map_id_no_metadata_warned: set[str] = set()


class MapData(BaseModel):
    meth_name: str = ""
    id: str
    name: str
    tag: str = ""
    year: int = 0
    pretty_name: str = ""
    short_name: str = ""
    allies: AnyFaction
    axis: AnyFaction
    allies_direction: CardinalDirection

    @model_validator(mode="after")
    def set_meth_name(self) -> "MapData":
        metadata = HLLV_MAP_METADATA
        meta = metadata.get(self.id)
        if meta is not None:
            self.meth_name = meta.get("meth_name", self.meth_name)
            self.tag = meta.get("tag", self.tag)
            self.year = meta.get("year", self.year)
            self.pretty_name = meta.get("pretty_name", self.pretty_name)
            self.short_name = meta.get("short_name", self.short_name)
        elif self.id not in _map_id_no_metadata_warned:
            logger.warning("No metadata found for map ID: %s", self.id)
            _map_id_no_metadata_warned.add(self.id)

        if not self.meth_name:
            self.meth_name = to_method_name(self.id)
        return self

    def to_constructor(self) -> str:
        template = HLLV_MAP_CONSTRUCTOR_TEMPLATE
        return template.format(map=self)


def get_all_maps() -> Iterator[MapMetaDataAsset]:
    for map_dir in HLLV_MAP_DIRS:
        for map_meta, _ in find_objects_in_dir(
            local_to_abs_path(map_dir / "MetaData", add_ext=False),
            lambda obj: obj.type == "MapMetaDataAsset",
            obj_type=MapMetaDataAsset,
            glob_pattern="*MapMeta.json",
        ):
            yield map_meta
            break
        else:
            logger.error(
                "No metadata found for map: %s",
                map_dir.name or map_dir,
            )


def get_map_data(map_meta: MapMetaDataAsset) -> MapData:
    props = map_meta.properties
    return MapData(
        id=props.map_id,
        name=str(props.map_friendly_name),
        short_name=props.map_id.upper(),
        allies=props.allies_faction.to_hllv_faction(),
        axis=props.axis_faction.to_hllv_faction(),
        allies_direction=props.get_direction(),
    )


def get_all_map_data() -> Iterator[MapData]:
    for map_meta in get_all_maps():
        yield get_map_data(map_meta)


def main() -> None:
    set_root_path(HLLV_METADATA_PATH)

    maps = list(get_all_map_data())
    map_constructors = [map_.to_constructor() for map_ in maps]

    inject_code(
        HLLV_MAP_OUTPUT_PATH,
        "hllv maps",
        "\n\n".join(map_constructors),
    )

    save_meta(HLLV_MAP_METADATA_PATH, MapMetaData, HLLV_MAP_METADATA)


class MapMetaData(TypedDict):
    meth_name: NotRequired[str]
    year: int
    tag: str
    pretty_name: str
    short_name: str


HLLV_MAP_METADATA_PATH = Path("./scripts/extract/meta/hllv/maps.json")
HLLV_MAP_METADATA: dict[str, MapMetaData] = load_meta(
    HLLV_MAP_METADATA_PATH,
    MapMetaData,
)

if __name__ == "__main__":
    main()
