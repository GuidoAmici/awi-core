#!/usr/bin/env python3
"""
Initialize a fresh AWI instance.

_system/ already exists (shipped with source code).
This script only sets up _data/ — the user's private layer.
"""

import subprocess
import sys
from pathlib import Path


SUBMODULES_MD = """\
# AWI Submodule Map

> Update this diagram and registry whenever submodules are added, removed, or restructured.

## Registry

### AWI — direct submodules

| Path | Local path | GitHub Repo | Type | Branch tracked | Clone status |
|---|---|---|---|---|---|

> Use /new-client <name> to add a client. Use /awi-user to add a user.
"""


def init_data(path: Path = Path(".")):
    path = path.resolve()

    # Create _data/ subdirs
    (path / "_data" / "organizations").mkdir(parents=True, exist_ok=True)
    (path / "_data" / "users").mkdir(parents=True, exist_ok=True)

    # Create submodules registry
    submodules_path = path / "_data" / "submodules.md"
    if not submodules_path.exists():
        submodules_path.write_text(SUBMODULES_MD)

    print("_data/ initialized.")
    print("  _data/organizations/   — organization submodules go here")
    print("  _data/users/     — user submodules go here")
    print("  _data/submodules.md — submodule registry")


if __name__ == "__main__":
    init_data()
