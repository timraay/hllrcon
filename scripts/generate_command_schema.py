"""Script to generate a JSON schema of all available RCON commands for the HLL server.

To run this script, ensure the `HLL_HOST`, `HLL_PORT`, and `HLL_PASSWORD` environment
variables are set.
Then, run `uv run scripts/generate_command_schema.py` in your terminal. The output will
be saved to `commands_schema.json`.
"""

import asyncio
import logging

import aiofiles
from pydantic import RootModel

from hllrcon.connection import RconConnection
from hllrcon.responses import GetCommandDetailsResponse
from scripts import HLL_SERVER_CREDENTIALS

logging.basicConfig(level=logging.INFO)


AllCommandDetails = RootModel[list[GetCommandDetailsResponse]]


async def main() -> None:
    if not HLL_SERVER_CREDENTIALS:
        msg = "Server credentials must be set in the environment variables."
        raise ValueError(msg)

    conn = await RconConnection.connect(**HLL_SERVER_CREDENTIALS)

    all_commands = await conn.get_commands()
    all_command_details = AllCommandDetails(
        await asyncio.gather(
            *(conn.get_command_details(entry.id) for entry in all_commands.entries),
        ),
    )

    async with aiofiles.open("commands_schema.json", "w", encoding="utf-8") as f:
        content = all_command_details.model_dump_json(indent=2)
        await f.write(content)


if __name__ == "__main__":
    asyncio.run(main())
