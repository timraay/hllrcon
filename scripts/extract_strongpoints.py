# ruff: noqa: T201

import json
from pathlib import Path
from typing import NamedTuple


class Strongpoint(NamedTuple):
    center: tuple[float, float, float]
    radius: float


def sort_key_horizontal(sp: Strongpoint) -> float:
    return (round(sp.center[0] / 40000) * 40000) + (sp.center[1] / 40000)


def sort_key_vertical(sp: Strongpoint) -> float:
    return (round(sp.center[1] / 40000) * 40000) + (sp.center[0] / 40000)


def main() -> None:
    content = json.loads(Path("scripts/extract_strongpoints.json").read_text())
    strongpoints: list[Strongpoint] = []
    for actor in content:
        if actor["Name"] == "TriggerShape" and actor["Outer"].startswith(
            "SphereSectorCaptureBooster",
        ):
            props = actor["Properties"]
            center = props["RelativeLocation"]
            radius = props.get("SphereRadius", 1000) * props.get(
                "RelativeScale3D",
                {},
            ).get("X", 1.0)

            strongpoints.append(
                Strongpoint(
                    center=(center["X"], center["Y"], center["Z"]),
                    radius=radius,
                ),
            )

    if len(strongpoints) != 15:
        msg = f"Expected 15 strongpoints, got {len(strongpoints)}"
        raise ValueError(msg)

    all_x = [sp.center[0] for sp in strongpoints]
    dx = max(all_x) - min(all_x)
    if dx > 120000:
        strongpoints.sort(key=sort_key_horizontal)
    else:
        strongpoints.sort(key=sort_key_vertical)

    for strongpoint in strongpoints:
        print(f", center={strongpoint.center}, radius={strongpoint.radius}")


if __name__ == "__main__":
    main()
