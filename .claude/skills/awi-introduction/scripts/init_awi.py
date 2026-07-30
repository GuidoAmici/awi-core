#!/usr/bin/env python3
"""
Initialize a fresh AWI instance.

_system/ already exists (shipped with source code).
This script only sets up _data/ — the user's private layer.
"""

import subprocess
import sys
from pathlib import Path




def init_data(path: Path = Path(".")):
    path = path.resolve()

    # Create _data/ subdirs
    (path / "_data" / "organizations").mkdir(parents=True, exist_ok=True)
    (path / "_data" / "users").mkdir(parents=True, exist_ok=True)

    print("_data/ initialized.")
    print("  _data/organizations/   — organization submodules go here")
    print("  _data/users/     — user submodules go here")


if __name__ == "__main__":
    init_data()
