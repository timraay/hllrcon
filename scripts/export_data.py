import json
from collections.abc import Hashable
from inspect import isclass
from pathlib import Path
from typing import Any, Literal, TypedDict

from pydantic import TypeAdapter
from pydantic.alias_generators import to_snake

import hllrcon.data
from hllrcon import __version__
from hllrcon.data._utils import IndexedBaseModel

OUTPUT_DIR = Path("dist/")
DATA_OUTPUT_NAME = "data.{game_name}.json"
SCHEMA_OUTPUT_NAME = "data.{game_name}.schema.json"
SCHEMA_URL = (
    "https://github.com/timraay/hllrcon/releases/download/"
    + __version__
    + "/data.{game_name}.schema.json"
)

GameName = Literal["hll", "hllv"]


def get_model_classes(game_name: GameName) -> list[type[IndexedBaseModel]]:
    return [
        model_cls
        for model_cls in vars(hllrcon.data).values()
        if isclass(model_cls)
        and issubclass(model_cls, IndexedBaseModel)
        and to_snake(model_cls.__name__).split("_")[0] == game_name
    ]


Models = dict[Hashable, IndexedBaseModel]
ModelMap = dict[str, Models]
ModelMapTypes = dict[str, type[dict[Hashable, type[IndexedBaseModel]]]]


def get_model_map(game_name: GameName) -> tuple[ModelMap, ModelMapTypes]:
    model_classes = get_model_classes(game_name)

    output: ModelMap = {}
    output_types: ModelMapTypes = {}

    for model_cls in model_classes:
        model_name = to_snake(model_cls.__name__).removeprefix(f"{game_name}_")

        output_types[model_name] = dict[Any, model_cls]  # type: ignore[valid-type]

        models: Models = {}
        output[model_name] = models
        for model in model_cls.all():
            models[model.id] = model

    return output, output_types


def write_data(game_name: GameName) -> None:
    output, output_types = get_model_map(game_name)

    output_type = TypedDict(  # type: ignore[misc]
        "ModelMap",
        output_types,
    )

    output_type_with_schema = TypedDict(
        "ModelMap",
        {
            "$schema": str,
            **output_types,  # type: ignore[misc]
        },
    )

    OUTPUT_DIR.mkdir(exist_ok=True)

    data_output_path = OUTPUT_DIR / DATA_OUTPUT_NAME.format(game_name=game_name)
    schema_output_path = OUTPUT_DIR / SCHEMA_OUTPUT_NAME.format(game_name=game_name)
    schema_url = SCHEMA_URL.format(game_name=game_name)

    with data_output_path.open("wb") as f:
        f.truncate(0)
        f.write(
            TypeAdapter(output_type_with_schema).dump_json(
                {"$schema": schema_url, **output},  # type: ignore[typeddict-item]
                indent=None,
            ),
        )

    with schema_output_path.open("w", encoding="utf-8") as f:
        f.truncate(0)
        schema = TypeAdapter(output_type).json_schema(mode="serialization")
        json.dump(schema, f, indent=None)


def main() -> None:
    for game_name in ("hll", "hllv"):
        write_data(game_name)


if __name__ == "__main__":
    main()
