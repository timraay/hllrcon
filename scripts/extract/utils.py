import json
import re
from collections.abc import Collection
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar

from pydantic import TypeAdapter

from hllrcon.data.factions import AnyFaction
from hllrcon.data.roles import AnyRole
from hllrcon.data.teams import AnyTeam


def inject_code(fp: Path, marker: str, code: str) -> None:
    escaped_marker = re.escape(marker)
    regexp = re.compile(
        (
            rf'([ \t]*)### *INJECT *"{escaped_marker}" *START *\n'
            rf'(?:[\w\W]*\n[ \t]*### *INJECT *"{escaped_marker}" * END)?'
        ),
    )

    content = fp.read_text("utf-8")

    # First assert that the marker exists in the file
    if not regexp.search(content):
        msg = f'Marker "{marker}" not found in file {fp}.'
        raise ValueError(msg)

    new_content = regexp.sub(
        f'\\1### INJECT "{marker}" START\n\n{code}\n\n\\1### INJECT "{marker}" END',
        content,
    )

    fp.write_text(new_content, "utf-8")


def indent_text(text: str, spaces: int) -> str:
    if spaces == 0:
        return text

    indent_str = " " * spaces
    return "\n".join(
        indent_str + line if line.strip() else "" for line in text.splitlines()
    )


def stringify_list(items: list[str], indent: int = 0) -> str:
    if not items:
        return indent_text("[]", indent)

    output = "[\n"

    for item in items:
        output += indent_text(item.rstrip() + ",", 4) + "\n"

    output += "]"

    return indent_text(output, indent)


def stringify_dict(d: dict[Any, Any], indent: int = 0) -> str:
    if not d:
        return indent_text("{}", indent)

    output = "{\n"

    for key, value in d.items():
        output += indent_text(f"{key}: {value},", 4) + "\n"

    output += "}"

    return indent_text(output, indent)


def stringify_enum_member(member: Enum) -> str:
    return f"{member.__class__.__name__}.{member.name}"


def stringify_team(team: AnyTeam) -> str:
    return f"{type(team).__name__}.{team.name.upper()}"


def stringify_faction(faction: AnyFaction) -> str:
    return f"{type(faction).__name__}.{faction.short_name.upper()}"


def stringify_factions(factions: Collection[AnyFaction], indent: int = 0) -> str:
    if len(factions) == 0:
        return indent_text("{}", indent)

    factions_str = [
        f"{type(f).__name__}.{f.short_name}"
        for f in sorted(factions, key=lambda x: x.id)
    ]

    if len(factions) <= 2:
        return indent_text("{" + ", ".join(factions_str) + "}", indent)

    return indent_text("{\n    " + ",\n    ".join(factions_str) + ",\n}", indent)


def stringify_role(role: AnyRole) -> str:
    role_name = role.pretty_name.replace(" ", "_").replace("-", "_").upper()
    return f"{type(role).__name__}.{role_name}"


def to_method_name(s: str) -> str:
    s = (
        s.upper()
        .replace("/ ", "_")
        .replace("/", "_")
        .replace("-", "_")
        .replace(" ", "_")
        .replace("[", "_")
        .replace("]", "_")
        .replace(".", "_")
        .replace("(", "")
        .replace(")", "")
    )

    # replace non-ASCII characters
    s = re.sub(r"[^A-Z0-9_]", "_", s)

    # Strip underscores
    s = s.strip("_")

    # replace starting digit with underscore
    if s and s[0].isdigit():
        s = "_" + s

    return s


T = TypeVar("T")


def load_meta(fp: Path, validation_cls: type[T]) -> dict[str, T]:
    if not fp.exists():
        msg = f"Metadata not found: {fp}"
        raise FileNotFoundError(msg)

    t = dict[str, validation_cls]  # type: ignore[valid-type]

    data = json.loads(fp.read_text(encoding="utf-8"))
    data.pop("$schema", None)  # Remove the $schema key if it exists

    return TypeAdapter(t).validate_python(data)


def save_meta(fp: Path, validation_cls: type[T], data: dict[str, T]) -> None:
    t = dict[str, validation_cls]  # type: ignore[valid-type]
    adapter = TypeAdapter(t)
    out = adapter.dump_python(data, mode="json")
    out["$schema"] = f"../_schemas/{fp.stem}.schema.json"

    fp.write_text(json.dumps(out, indent=2), encoding="utf-8")
    save_meta_schema(
        fp.parent.parent / f"_schemas/{fp.stem}.schema.json",
        validation_cls,
    )


def save_meta_schema(fp: Path, validation_cls: type[T]) -> None:
    t = dict[str, str | validation_cls]  # type: ignore[valid-type]
    adapter = TypeAdapter(t)
    schema = adapter.json_schema()
    fp.write_text(json.dumps(schema, indent=2), encoding="utf-8")
