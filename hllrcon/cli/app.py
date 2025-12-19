import asyncio
from ipaddress import IPv4Address
from typing import Annotated

import typer

from hllrcon.cli.main import main

app = typer.Typer()


@app.command()
def app_main(
    address: Annotated[
        IPv4Address,
        typer.Argument(
            parser=IPv4Address,
            help="IPv4 address",
        ),
    ],
    port: Annotated[
        int,
        typer.Argument(..., help="RCON port number", min=1, max=65535),
    ],
    password: Annotated[str, typer.Argument(..., help="RCON password")],
) -> None:
    asyncio.run(main(str(address), port, password))
