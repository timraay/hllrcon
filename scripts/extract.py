import logging
import subprocess

from scripts.extract import loadout_items, loadouts, role_progression, vehicles

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Extracting loadout items...")
    loadout_items.main()
    logger.info("Extracting loadouts...")
    loadouts.main()
    logger.info("Extracting role progression...")
    role_progression.main()
    logger.info("Extracting vehicles...")
    vehicles.main()

    # Run ruff to format the generated files
    subprocess.run(
        ["ruff", "format", "hllrcon/data"],  # noqa: S607
        check=True,
    )


if __name__ == "__main__":
    main()
