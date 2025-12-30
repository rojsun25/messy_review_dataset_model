#!/usr/bin/env python3
"""Stop and remove the local Airflow environment (including volumes)."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMPOSE_FILE = ROOT / "docker-compose.yaml"


def main() -> None:
    subprocess.run(["docker", "compose", "-f", str(COMPOSE_FILE), "down", "--volumes", "--remove-orphans"], check=False)
    print("Removed containers and volumes.")


if __name__ == "__main__":
    main()
