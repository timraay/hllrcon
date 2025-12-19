import typer
from rich import print as pprint
from rich.progress import Progress, SpinnerColumn, TextColumn

from hllrcon.exceptions import HLLConnectionError
from hllrcon.rcon import Rcon


async def main(address: str, port: int, password: str) -> None:
    rcon = Rcon(str(address), port, password)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(
            description=f" Connecting to {address}:{port}...",
            total=None,
        )

        try:
            await rcon.wait_until_connected()
        except HLLConnectionError as e:
            pprint(
                f" [bold red]✗[/bold red]  Failed to connect to {address}:{port}."
                f"\n    [italic red]{e}[/italic red]",
            )
            raise typer.Exit(code=1) from None
        except TimeoutError:
            pprint(
                f" [bold red]✗[/bold red]  Connection to {address}:{port} timed out.",
            )
            raise typer.Exit(code=1) from None

    pprint(f" [bold green]✓[/bold green]  Successfully connected to {address}:{port}!")
