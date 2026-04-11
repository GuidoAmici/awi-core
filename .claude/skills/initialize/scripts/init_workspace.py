#!/usr/bin/env python3
"""Scaffold a new AWI workspace repo for a company or client."""

import argparse
import json
import subprocess
from pathlib import Path

AGENDA_FOLDERS = [
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

CLAUDE_MD = """\
# {name_title} — AWI Workspace

**All vault rules, structure, taxonomy, and commands are in the AWI engine.**
Point Claude Code to the parent AWI repo for skills and workflow documentation.

## This workspace

- **Agenda:** `_documentation/_agenda/` — tasks, projects, people, daily, weekly
- **Context:** `_documentation/_context/` — wiki, codebase stubs, user profiles
- **Codebase:** `_codebase/` — app submodules

## Get current date

```bash
bash <awi-path>/.claude/hooks/get-datetime.sh full
```
"""


def init_workspace(name: str, parent_path: Path):
    workspace_name = f"{name}-workspace"
    path = (parent_path / workspace_name).resolve()

    if path.exists():
        print(f"Error: {path} already exists.")
        return

    # Create _documentation/_agenda folders
    for folder in AGENDA_FOLDERS:
        (path / "_documentation" / "_agenda" / folder).mkdir(parents=True, exist_ok=True)

    # Create _documentation/_context folders
    for folder in CONTEXT_FOLDERS:
        (path / "_documentation" / "_context" / folder).mkdir(parents=True, exist_ok=True)

    # Create _codebase/
    (path / "_codebase").mkdir(parents=True, exist_ok=True)

    # Create CLAUDE.md
    name_title = name.title()
    (path / "CLAUDE.md").write_text(CLAUDE_MD.format(name_title=name_title))

    # Create .gitignore
    (path / ".gitignore").write_text(GITIGNORE)

    # Initialize git
    subprocess.run(["git", "init"], cwd=path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"cos: initialize {name}-workspace [confidence: 1.00]"],
        cwd=path,
        check=True,
    )

    print(f"Initialized {workspace_name} at {path}")
    print()
    print("Structure:")
    print(f"  _documentation/_agenda/  ← {', '.join(AGENDA_FOLDERS[:4])}, ...")
    print(f"  _documentation/_context/ ← {', '.join(CONTEXT_FOLDERS)}")
    print(f"  _codebase/               ← app submodules go here")
    print()
    print("Next steps:")
    print(f"  1. cd {path}")
    print(f"  2. claude")
    print(f"  3. /awi-user-create <username>")
    print(f"  4. /awi-user-login <username>")

    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold an AWI workspace repo")
    parser.add_argument("name", help="Workspace name (e.g. newhaze, afin, guido)")
    parser.add_argument("path", nargs="?", default="..", help="Parent directory (default: ../)")
    args = parser.parse_args()

    init_workspace(args.name, Path(args.path))
