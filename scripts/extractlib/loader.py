import json
import re
from functools import cache
from os import PathLike
from pathlib import Path
from typing import Annotated, Any, Generic

from pydantic import BaseModel, ConfigDict, Field, GetCoreSchemaHandler
from pydantic.alias_generators import to_pascal
from pydantic_core import CoreSchema, core_schema
from typing_extensions import TypeVar

from scripts import HLL_METADATA_PATH

RE_OBJECT_PATH = re.compile(r"^(?P<path>.+?)(?:\.(?P<index>\d+))?$")
RE_ASSET_PATH = re.compile(r"^(?P<path>.+)\.(?P<name>.+)$")

ModelT = TypeVar("ModelT", bound="Model", default="Model")
ModelT_co = TypeVar("ModelT_co", bound="Model", default="Model", covariant=True)
ObjectT = TypeVar(
    "ObjectT",
    bound="Object[Any]",
    default="Object[Any]",
)
ObjectT_co = TypeVar(
    "ObjectT_co",
    bound="Object[Any]",
    default="Object[Any]",
    covariant=True,
)


_root_path = HLL_METADATA_PATH


def set_root_path(path: Path) -> None:
    global _root_path  # noqa: PLW0603
    _root_path = path


def get_root_path() -> Path:
    return _root_path


def merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = base.copy()
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def local_to_abs_path(local_path: str | PathLike, *, add_ext: bool = True) -> Path:
    local_path_str = Path(local_path).as_posix()

    from scripts.extractlib.utils import game_switch  # noqa: PLC0415

    if local_path_str.startswith("/Game/"):
        game_name = game_switch("HLL", "HLLVietnam")
        local_path_str = f"./{game_name}/Content/" + local_path_str.removeprefix(
            "/Game/",
        )

    if local_path_str.startswith("/"):
        local_path_str = "." + local_path_str

    if add_ext and not local_path_str.endswith(".json"):
        local_path_str += ".json"

    return get_root_path() / local_path_str


@cache
def read_file(abs_path: Path) -> list[Any]:
    content = abs_path.read_text(encoding="utf-8")
    json_content = json.loads(content)
    if not isinstance(json_content, list) or len(json_content) == 0:
        msg = f"Expected a non-empty array in the JSON file: {abs_path}"
        raise TypeError(msg)
    return json_content


def load_raw_from_file(
    abs_path: Path,
    index_or_name: int | str,
) -> dict[str, Any]:
    json_content = read_file(abs_path)

    raw_obj: dict[str, Any]
    if isinstance(index_or_name, str):
        for raw_obj in json_content:
            if raw_obj.get("Name") == index_or_name:
                break
        else:
            msg = f"Name '{index_or_name}' not found in the JSON file: {abs_path}"
            raise ValueError(msg)
    elif isinstance(index_or_name, int):
        if not 0 <= index_or_name < len(json_content):
            msg = (
                f"Index {index_or_name} is out of bounds for the JSON file: {abs_path}"
            )
            raise IndexError(msg)
        raw_obj = json_content[index_or_name]
    else:
        msg = f"index_or_name must be either an int or a str, got {type(index_or_name)}"
        raise TypeError(msg)

    raw_obj.setdefault("Properties", {})

    plain_obj = Object[Any].model_validate(raw_obj)
    if plain_obj.super is not None:
        raw_super_obj = plain_obj.super.object_path.load_raw()
        raw_obj = merge_dicts(raw_super_obj, raw_obj)

    plain_obj = Object[Any].model_validate(raw_obj)
    if plain_obj.template is not None:
        raw_template_obj = plain_obj.template.object_path.load_raw()
        raw_obj = merge_dicts(raw_template_obj, raw_obj)

    return raw_obj


def load_object_from_file(
    abs_path: Path,
    index_or_name: int | str,
    obj_type: type["ObjectT"],
) -> ObjectT:
    raw_obj = load_raw_from_file(abs_path, index_or_name)
    return obj_type.model_validate(raw_obj)


def load_local(
    local_path: Path,
    index_or_name: int | str,
    obj_type: type["ObjectT"],
) -> ObjectT:
    abs_path = local_to_abs_path(local_path)
    return load_object_from_file(abs_path, index_or_name, obj_type)


class Model(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_pascal,
        validate_by_name=True,
        frozen=True,
    )


class ObjectPath(str):
    __slots__ = ("obj_index", "obj_path")

    obj_path: str | None
    obj_index: str | int

    def _parse_value(self, value: str) -> None:
        match = RE_OBJECT_PATH.match(value)
        if not match:
            msg = f"Invalid object path: {value}"
            raise ValueError(msg)
        groupdict = match.groupdict()

        self.obj_path = str(groupdict["path"])
        self.obj_index = int(groupdict["index"] or "0")

    def __init__(self, value: str) -> None:
        if value == "None":
            self.obj_path = None
            self.obj_index = 0

        else:
            self._parse_value(value)

    def is_none(self) -> bool:
        return self.obj_path is None

    def load_raw(self) -> dict[str, Any]:
        if self.obj_path is None:
            msg = "Cannot load object from 'None' path"
            raise ValueError(msg)

        path = local_to_abs_path(self.obj_path)
        return load_raw_from_file(path, self.obj_index)

    def load(self, obj_type: type[ObjectT]) -> ObjectT:
        if self.obj_path is None:
            msg = "Cannot load object from 'None' path"
            raise ValueError(msg)

        path = local_to_abs_path(self.obj_path)
        return load_object_from_file(path, self.obj_index, obj_type)

    def __str__(self) -> str:
        return (
            f"{self.obj_path}.{self.obj_index}" if self.obj_path is not None else "None"
        )

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))


class ObjectReference(Model, Generic[ObjectT_co]):
    object_name: str
    object_path: ObjectPath

    def is_none(self) -> bool:
        return self.object_path.is_none()

    def is_script(self) -> bool:
        return self.object_path.startswith("/Script/")

    def get(self, obj_type: type[ObjectT_co]) -> ObjectT_co:
        return self.object_path.load(obj_type)


class Object(Model, Generic[ModelT_co]):
    type: str
    name: str
    flags: str
    class_: Annotated[str, Field(validation_alias="Class")]
    outer: ObjectReference | None = None
    super: ObjectReference | None = None
    template: ObjectReference | None = None
    properties: ModelT_co

    def get_name(self) -> str:
        return f"{self.type}'{self.name}'"


class AssetPath(ObjectPath):
    def _parse_value(self, value: str) -> None:
        match = RE_ASSET_PATH.match(value)
        if not match:
            msg = f"Invalid asset path: {value}"
            raise ValueError(msg)
        groupdict = match.groupdict()

        self.obj_path = str(groupdict["path"])
        self.obj_index = str(groupdict["name"])


class AssetReference(Model, Generic[ObjectT_co]):
    asset_path_name: AssetPath
    sub_path_string: str | None = None

    def is_none(self) -> bool:
        return self.asset_path_name.is_none()

    def get(self, asset_type: type[ObjectT_co]) -> ObjectT_co:
        return self.asset_path_name.load(asset_type)
