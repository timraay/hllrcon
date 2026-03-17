import json
from collections.abc import Hashable
from inspect import isclass
from pathlib import Path
from typing import Any, TypedDict

from pydantic import TypeAdapter
from pydantic.alias_generators import to_snake

import hllrcon.data
from hllrcon import __version__
from hllrcon.data._utils import IndexedBaseModel

OUTPUT_DIR = Path("dist/")
DATA_OUTPUT_PATH = OUTPUT_DIR / "data.json"
SCHEMA_OUTPUT_PATH = OUTPUT_DIR / "data.schema.json"
SCHEMA_URL = f"https://github.com/timraay/hllrcon/releases/download/{__version__}/data.schema.json"


def get_model_classes() -> list[type[IndexedBaseModel]]:
    return [
        model_cls
        for model_cls in vars(hllrcon.data).values()
        if isclass(model_cls) and issubclass(model_cls, IndexedBaseModel)
    ]


Models = dict[Hashable, IndexedBaseModel]
ModelMap = dict[str, Models]


def main() -> None:
    model_classes = get_model_classes()

    output: ModelMap = {}
    output_types: dict[str, type[dict[Hashable, type[IndexedBaseModel]]]] = {}

    for model_cls in model_classes:
        model_name = to_snake(model_cls.__name__)

        output_types[model_name] = dict[Any, model_cls]

        models: Models = {}
        output[model_name] = models
        for model in model_cls.all():
            models[model.id] = model

    output_type = TypedDict(
        "ModelMap",
        output_types,
    )

    output_type_with_schema = TypedDict(
        "ModelMap",
        {
            "$schema": str,
            **output_types,
        },
    )

    OUTPUT_DIR.mkdir(exist_ok=True)

    with DATA_OUTPUT_PATH.open("wb") as f:
        f.truncate(0)
        f.write(
            TypeAdapter(output_type_with_schema).dump_json(
                {"$schema": SCHEMA_URL, **output},
                indent=2,
            ),
        )

    with SCHEMA_OUTPUT_PATH.open("w", encoding="utf-8") as f:
        f.truncate(0)
        schema = TypeAdapter(output_type).json_schema(mode="serialization")
        json.dump(schema, f, indent=2)


if __name__ == "__main__":
    main()
