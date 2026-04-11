#!/usr/bin/env python3
"""Initialize an AWI (Agentic Workflow Integrator) vault with folder structure and git."""

import argparse
import subprocess
from pathlib import Path

SCHEDULE_FOLDERS = [
    "tasks", "projects", "people", "ideas",
    "daily", "weekly", "outputs", "planning",
    "user-profile-inference",
]

CONTEXT_FOLDERS = ["users", "codebase"]

GITIGNORE = """\
# Obsidian
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/plugins/
.obsidian/core-plugins-migration.json

# macOS
.DS_Store

# Temporary files
*.tmp
"""

CONTEXT_INDEX = """\
# Context Files

Reference documents for LLM context.

## Available Context

- `writing-style.md` - Voice, tone, and writing preferences
- `business-profile.md` - Company/work context
- `users/` - Vault user login profiles

## Usage

Check relevant context files before writing or complex tasks.
"""


def init_vault(path: Path):
    path = path.resolve()

    # Create _documentation/_schedule folders
    for folder in SCHEDULE_FOLDERS:
        (path / "_documentation" / "_schedule" / folder).mkdir(parents=True, exist_ok=True)

    # Create _documentation/_context folders
    for folder in CONTEXT_FOLDERS:
        (path / "_documentation" / "_context" / folder).mkdir(parents=True, exist_ok=True)

    # Create _context/_index.md
    (path / "_documentation" / "_context" / "_index.md").write_text(CONTEXT_INDEX)

    # Create .gitignore
    (path / ".gitignore").write_text(GITIGNORE)

    # Initialize git if not already a repo
    if not (path / ".git").exists():
        subprocess.run(["git", "init"], cwd=path, check=True)

    # Initial commit
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "cos: initialize AWI vault structure [confidence: 1.00]"],
        cwd=path,
        check=True,
    )

    print(f"Initialized AWI vault at {path}")
    print(f"Created: _documentation/_schedule/{{{', '.join(SCHEDULE_FOLDERS)}}}")
    print(f"Created: _documentation/_context/{{{', '.join(CONTEXT_FOLDERS)}}}")
    print()
    print("Next steps:")
    print("  1. Open this folder as an Obsidian vault")
    print("  2. Launch Claude Code: claude")
    print("  3. Create your user: /awi-user-create <username>")
    print("  4. Log in: /awi-user-login <username>")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize an AWI vault")
    parser.add_argument("path", nargs="?", default=".", help="Vault path (default: current directory)")
    args = parser.parse_args()

    init_vault(Path(args.path))
