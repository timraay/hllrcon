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

**hllrcon** is an asynchronous Python implementation of the Hell Let Loose RCON protocol.  
It allows you to interact with your HLL servers programmatically, supporting modern Python async features and robust error handling.

## Features

- Full async/await support
- Command execution and response parsing
- Connection pooling
- Well-typed and tested

## Installation

```sh
pip install hllrcon
```

## Usage
```py
import asyncio
from hllrcon import Rcon


async def main():
    # Initialize client
    rcon = Rcon(
        host="127.0.0.1",
        port=12345,
        password="your_rcon_password",
    )

    # Send commands. The client will (re)connect for you.
    await rcon.broadcast("Hello, HLL!")
    players = await rcon.get_players()

    # Close the connection
    rcon.disconnect()


    # Alternatively, use the context manager interface to avoid
    # having to manually disconnect.
    async with rcon.connect():
        assert rcon.is_connected() is True
        await rcon.get_players("Hello, HLL!")


if __name__ == '__main__':
    # Run the program
    asyncio.run(main())
```

# License

This project is licensed under the MIT License. See [`LICENSE`](/LICENSE) for details.
