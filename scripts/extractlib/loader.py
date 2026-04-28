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
from scripts.extractlib.utils import merge_dicts

RE_OBJECT_PATH = re.compile(r"^(?P<path>.+?)(?:\.(?P<index>\d+))?$")
RE_ASSET_PATH = re.compile(r"^(?P<path>.+)\.(?P<name>.+)$")

ModelT = TypeVar("ModelT", bound="Model", default="Model")
ObjectT = TypeVar("ObjectT", bound="Object[Any]", default="Object[Any]")

_root_path = HLL_METADATA_PATH


def set_root_path(path: Path) -> None:
    global _root_path  # noqa: PLW0603
    _root_path = path


def get_root_path() -> Path:
    return _root_path


def local_to_abs_path(local_path: str | PathLike) -> Path:
    local_path_str = Path(local_path).as_posix()

    if local_path_str.startswith("/Game/"):
        local_path_str = "./HLL/Content/" + local_path_str.removeprefix("/Game/")

    if local_path_str.startswith("/"):
        local_path_str = "." + local_path_str

    return get_root_path() / (local_path_str + ".json")


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
    index: int,
) -> dict[str, Any]:
    json_content = read_file(abs_path)
    if not 0 <= index < len(json_content):
        msg = f"Index {index} is out of bounds for the JSON file: {abs_path}"
        raise IndexError(msg)
    raw_obj: dict[str, Any] = json_content[index]

    plain_obj = Object[Any].model_validate(raw_obj)
    if plain_obj.template is not None:
        raw_template_obj = plain_obj.template.object_path.load_raw()
        raw_obj = merge_dicts(raw_template_obj, raw_obj)

    return raw_obj


def load_object_from_file(
    abs_path: Path,
    index: int,
    obj_type: type["ObjectT"],
) -> ObjectT:
    raw_obj = load_raw_from_file(abs_path, index)
    return obj_type.model_validate(raw_obj)


def load_asset(abs_path: Path, obj_type: type[ObjectT]) -> ObjectT:
    return load_object_from_file(abs_path, 0, obj_type)


class Model(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_pascal,
        validate_by_name=True,
    )


class ObjectPath(str):
    __slots__ = ("obj_index", "obj_path")

    def __init__(self, value: str) -> None:
        match = RE_OBJECT_PATH.match(value)
        if not match:
            msg = f"Invalid object path: {value}"
            raise ValueError(msg)
        groupdict = match.groupdict()

        self.obj_path = str(groupdict["path"])
        self.obj_index = int(groupdict["index"] or "0")

    def load_raw(self) -> dict[str, Any]:
        path = get_root_path() / (self.obj_path + ".json")
        return load_raw_from_file(path, self.obj_index)

    def load(self, obj_type: type[ObjectT]) -> ObjectT:
        path = get_root_path() / (self.obj_path + ".json")
        return load_object_from_file(path, self.obj_index, obj_type)

    def __str__(self) -> str:
        return f"{self.obj_path}.{self.obj_index}"

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))


class ObjectReference(Model, Generic[ObjectT]):
    object_name: str
    object_path: ObjectPath

    def get(self, obj_type: type[ObjectT]) -> ObjectT:
        return self.object_path.load(obj_type)


class Object(Model, Generic[ModelT]):
    type: str
    name: str
    flags: str
    class_: Annotated[str, Field(validation_alias="Class")]
    outer: ObjectReference | None = None
    template: ObjectReference | None = None
    properties: ModelT


class AssetPath(str):
    __slots__ = ("asset_name", "asset_path")

    def __init__(self, value: str) -> None:
        match = RE_ASSET_PATH.match(value)
        if not match:
            msg = f"Invalid asset path: {value}"
            raise ValueError(msg)
        groupdict = match.groupdict()

        self.asset_path = str(groupdict["path"])
        self.asset_name = str(groupdict["name"])

    def load_raw(self) -> dict[str, Any]:
        abs_path = local_to_abs_path(self.asset_path)
        return load_raw_from_file(abs_path, 0)

    def load(self, obj_type: type[ObjectT]) -> ObjectT:
        abs_path = local_to_abs_path(self.asset_path)
        return load_object_from_file(abs_path, 0, obj_type)

    def __str__(self) -> str:
        return f"{self.asset_path}.{self.asset_name}"

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))


class AssetReference(Model, Generic[ObjectT]):
    asset_path_name: AssetPath
    sub_path_string: str | None = None

    def load(self, asset_type: type[ObjectT]) -> ObjectT:
        abs_path = local_to_abs_path(self.asset_path_name.asset_path)
        obj = load_object_from_file(abs_path, 0, asset_type)
        if obj.name != self.asset_path_name.asset_name:
            # Currently we assume that the asset is always the first object.
            # That might be a false assumption.
            msg = (
                f"Asset name mismatch: expected {self.asset_path_name.asset_name}, "
                f"got {obj.name} in asset path {abs_path}"
            )
            raise ValueError(msg)
        return obj
