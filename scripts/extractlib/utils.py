from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from scripts.extractlib.loader import Object, ObjectT, ObjectT_co, load_object_from_file


def find_objects_in_file(
    abs_path: Path,
    condition: Callable[[ObjectT_co], bool],
    obj_type: type[ObjectT],
    cond_obj_type: type[ObjectT_co] = Object[Any],  # type: ignore[assignment]
) -> Generator[ObjectT, None, None]:
    i = -1
    while True:
        i += 1
        try:
            obj = load_object_from_file(abs_path, i, cond_obj_type or Object[Any])
        except ValidationError:
            continue
        except IndexError:
            return None

        if condition(obj):  # type: ignore[arg-type]
            yield load_object_from_file(abs_path, i, obj_type)


def find_objects_in_dir(
    abs_dir_path: Path,
    condition: Callable[[ObjectT_co], bool],
    obj_type: type[ObjectT],
    cond_obj_type: type[ObjectT_co] = Object[Any],  # type: ignore[assignment]
    glob_pattern: str = "*.json",
) -> Generator[tuple[ObjectT, Path], None, None]:
    for abs_path in abs_dir_path.glob(glob_pattern):
        for obj in find_objects_in_file(
            abs_path,
            condition,
            obj_type,
            cond_obj_type=cond_obj_type,
        ):
            yield obj, abs_path
