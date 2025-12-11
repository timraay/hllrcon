<h1 align="center"><code>hllrcon</code> - Hell Let Loose RCON</h1>

<p align="center">
<a href="https://github.com/timraay/hllrcon/releases" target="_blank">
    <img src="https://img.shields.io/github/release/timraay/hllrcon.svg" alt="Release">
</a>
<a href="https://pypi.python.org/pypi/hllrcon" target="_blank">
    <img src="https://img.shields.io/pypi/v/hllrcon.svg" alt=PyPI>
</a>
<a href="https://codecov.io/gh/timraay/hllrcon" target="_blank">
    <img src="https://codecov.io/gh/timraay/hllrcon/graph/badge.svg?token=E60H3U7RQA" alt="Branch Coverage">
</a>
<a href="https://github.com/timraay/hllrcon/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/timraay/hllrcon.svg" alt="License">
</a>
<a href="https://github.com/timraay/hllrcon/graphs/contributors" target="_blank">
    <img src="https://img.shields.io/github/contributors/timraay/hllrcon.svg" alt="GitHub contributors">
</a>
<a href="https://github.com/timraay/hllrcon/issues" target="_blank">
    <img src="https://img.shields.io/github/issues/timraay/hllrcon.svg" alt="GitHub issues">
</a>
<a href="https://github.com/timraay/hllrcon/pulls" target="_blank">
    <img src="https://img.shields.io/github/issues-pr/timraay/hllrcon.svg" alt="GitHub pull requests">
</a>
<a href="https://github.com/timraay/hllrcon/stargazers" target="_blank">
    <img src="https://img.shields.io/github/stars/timraay/hllrcon.svg" alt="GitHub stars">
</a>
</p>

---

**hllrcon** is an asynchronous Python implementation of the [Hell Let Loose](https://www.hellletloose.com/game/hll) RCON protocol.  
It allows you to interact with your HLL servers programmatically, supporting modern Python async features and robust error handling.

## Features

- Full async/await support
- Command execution and response parsing
- Collection of vanilla maps, factions, weapons, and more
- Alternative interfaces for synchronous applications
- Well-typed and tested

## Installation

```sh
pip install hllrcon
```

## Usage
```py
import asyncio
from hllrcon import Rcon, Layer


async def main():
    # Initialize client
    rcon = Rcon(
        host="127.0.0.1",
        port=12345,
        password="your_rcon_password",
    )

    # Send commands. The client will (re)connect for you.
    await rcon.broadcast("Hello, HLL!")
    await rcon.change_map(Layer.STALINGRAD_WARFARE_DAY)
    players = await rcon.get_players()

    # Close the connection
    rcon.disconnect()


    # Alternatively, use the context manager interface to avoid
    # having to manually disconnect.
    async with rcon.connect():
        assert rcon.is_connected() is True
        await rcon.broadcast("Hello, HLL!")


if __name__ == "__main__":
    # Run the program
    asyncio.run(main())
```

For integration of synchronous applications, a `SyncRcon` class is provided.

```py
from hllrcon.sync import SyncRcon

rcon = SyncRcon(
    host="127.0.0.1",
    port=12345,
    password="your_rcon_password",
)

# Connect and send a broadcast message
with rcon.connect():
    rcon.broadcast("Hello, HLL!")
```

The library contains a swathe of details about in-game maps, factions, weapons, vehicles, and more. Below is just an example of what it might be used for.

```py
from hllron import Weapon

# Find a weapon by its ID
weapon_id = "COAXIAL M1919 [Stuart M5A1]"
weapon = Weapon.by_id(weapon_id)

# Print out whichever vehicle seat the attacker must have been in, if any
if weapon.vehicle:
    for seat in weapon.vehicle.seats:
        if weapon in seat.weapons:
            print("This weapon belongs to the", seat.type.name, "seat")
            break
```
```py
from hllrcon import Rcon, Map, Team

# Get the AA Network capture zone (SMDM, 3rd sector, 2nd capture zone)
sector = Layer.STMARIEDUMONT_WARFARE_DAY.sectors[2]
capture_zone = sector.capture_zones[1]
assert capture_zone.strongpoint.name == "AA Network"

# Get the current online players
rcon = Rcon(...)
players = await rcon.get_players()

# Calculate each team's capture strength towards the sector
strength = {Team.ALLIES: 0, Team.AXIS: 0}
for player in players.players:
    if player.faction is None:
        continue

    if player.world_position == (0.0, 0.0, 0.0):
        # Player is dead. Note: Does not exclude players bleeding out
        continue

    # Grant 3 strength if inside the strongpoint
    if capture_zone.strongpoint.is_inside(player.world_position):
        strength[player.faction.team] += 3

    # Only grant 1 strength if inside the capture zone
    elif capture_zone.is_inside(player.world_position):
        strength[player.faction.team] += 1

# Print out the results
print("Allied cap weight:", strength[Team.ALLIES])
print("Axis cap weight:", strength[Team.AXIS])
```

# Versioning

This project largely follows [Semantic Versioning principles](https://semver.org/), i.e. `MAJOR.MINOR.PATCH`, with one notable difference in what can be guaranteed.

The SemVer specification states that breaking changes must only be implemented in major versions, whereas this library will have breaking changes in minor versions. Therefore, backwards compatibility cannot be guaranteed for minor releases.

- **MAJOR** - Reserved for when sweeping changes need to happen to the library.
- **MINOR** - Incremented whenever significant or breaking changes have to be made to the library, including adding support for major Hell Let Loose updates.
- **PATCH** - Incremented for bug fixes and small game updates, generally guaranteeing backwards compatibility.


# License

This project is licensed under the MIT License. See [`LICENSE`](/LICENSE) for details.
