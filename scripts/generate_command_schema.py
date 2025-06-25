import asyncio
import json
import logging

from hllrcon.connection import RconConnection

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    # host = input("Address: ")
    # port = int(input("Port: "))
    # password = input("Password: ")
    host = "188.165.39.157"
    port = 7819
    password = "px2mg"

    conn = await RconConnection.connect(host=host, port=port, password=password)

    all_commands = await conn.get_commands()
    all_command_details = await asyncio.gather(
        *(conn.get_command_details(entry["iD"]) for entry in all_commands["entries"])
    )

    with open("commands_schema.json", "w", encoding="utf-8") as f:
        json.dump(all_command_details, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())
