import tomllib
import types
from pathlib import Path

import hllrcon


def test_all_imports_explicitly_defined() -> None:
    expected = {
        name
        for name, obj in vars(hllrcon).items()
        if not name.startswith("_") and not isinstance(obj, types.ModuleType)
    }

    expected.add("__version__")

    actual = set(hllrcon.__all__)
    assert expected == actual, "hllrcon.__all__ is not defined correctly"


def test_version_matches_pyproject() -> None:
    with Path("pyproject.toml").open("rb") as f:
        pyproject_data = tomllib.load(f)

    expected_version = pyproject_data["project"]["version"]
    assert hllrcon.__version__ == expected_version, (
        "Version mismatch with pyproject.toml"
    )
