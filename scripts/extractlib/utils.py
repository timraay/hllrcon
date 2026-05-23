from collections.abc import Callable, Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, TypeVar

from pydantic import ValidationError

from scripts import HLL_METADATA_PATH, HLLV_METADATA_PATH
from scripts.extractlib.loader import (
    Object,
    ObjectT,
    ObjectT_co,
    get_root_path,
    load_object_from_file,
    set_root_path,
)


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


@contextmanager
def root_path_ctx(path: Path) -> Generator[Path, None, None]:
    curr_path = get_root_path()

    try:
        set_root_path(path)
        yield path
    finally:
        set_root_path(curr_path)


T = TypeVar("T")
U = TypeVar("U")


def game_switch(
    hll_value: T,
    hllv_value: U,
) -> T | U:
    if get_root_path() == HLL_METADATA_PATH:
        return hll_value
    if get_root_path() == HLLV_METADATA_PATH:
        return hllv_value
    msg = "Root path is neither HLL_METADATA_PATH nor HLLV_METADATA_PATH"
    raise ValueError(msg)
