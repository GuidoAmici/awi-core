#!/usr/bin/env python3
"""Initialize a chief-of-staff vault with folder structure and git."""

import argparse
import subprocess
from pathlib import Path

FOLDERS = ["tasks", "projects", "people", "ideas", "context", "daily", "weekly", "outputs"]

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

## Usage

Check relevant context files before writing or complex tasks.
"""


def init_vault(path: Path):
    path = path.resolve()

    # Create folders
    for folder in FOLDERS:
        (path / folder).mkdir(parents=True, exist_ok=True)

    # Create context/_index.md
    (path / "context" / "_index.md").write_text(CONTEXT_INDEX)

    # Create .gitignore
    (path / ".gitignore").write_text(GITIGNORE)

    # Initialize git if not already a repo
    if not (path / ".git").exists():
        subprocess.run(["git", "init"], cwd=path, check=True)

    # Initial commit
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "cos: initialize vault structure [confidence: 1.00]"],
        cwd=path,
        check=True,
    )

    print(f"Initialized vault at {path}")
    print(f"Created: {', '.join(FOLDERS)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize a chief-of-staff vault")
    parser.add_argument("path", nargs="?", default=".", help="Vault path (default: current directory)")
    args = parser.parse_args()

    init_vault(Path(args.path))
