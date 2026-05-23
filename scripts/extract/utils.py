import re
from collections.abc import Collection
from enum import Enum
from pathlib import Path
from typing import Any

from hllrcon.data.factions import Faction
from hllrcon.data.roles import Role


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


def stringify_factions(factions: Collection[Faction]) -> str:
    factions_str = [
        f"{type(f).__name__}.{f.short_name}"
        for f in sorted(factions, key=lambda x: x.id)
    ]

    return "{" + ", ".join(factions_str) + "}"


def stringify_role(role: Role) -> str:
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
