IS_CLI_INSTALLED = False
try:
    import typer  # noqa: F401
except ImportError:
    pass
else:
    from hllrcon.cli.app import app

    IS_CLI_INSTALLED = True


def main() -> None:
    if not IS_CLI_INSTALLED:
        message = (
            'To use the hllrcon command, please install "hllrcon[cli]":'
            '\n\n\tpip install "hllrcon[cli]"\n'
        )
        print(message)  # noqa: T201
        raise RuntimeError(message)

    # Run the CLI application
    app()
