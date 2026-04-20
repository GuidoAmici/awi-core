#!/usr/bin/env python3
"""Scaffold a new AWI client repo."""

import argparse
import subprocess
from pathlib import Path

AGENDA_FOLDERS = [
    "tasks", "projects", "people", "ideas",
    "daily", "weekly", "outputs", "planning",
    "user-profile-inference",
]

AGENDA_ABSTRACT = "Tasks, projects, people, daily notes, and outputs for this client.\n"

AGENDA_OVERVIEW = """\
Agenda folder for this client workspace.

## Structure

- tasks/       — atomic work items
- projects/    — time-bound initiatives
- people/      — person profiles and follow-ups
- ideas/       — brainstorming and mental models
- daily/       — daily notes (YYYY-MM-DD.md)
- weekly/      — weekly reviews (YYYY-WNN.md)
- outputs/     — deliverables and reports (YYYY-MM-DD-<slug>.md)
- planning/    — quarterly and annual goals
- user-profile-inference/ — session observations

All files use YAML frontmatter. See AWI INSTRUCTIONS.md for file formats.
"""

DOCUMENTATION_ABSTRACT = "Context files: writing style, business profile, wiki.\n"

CLAUDE_MD = """\
# {name_title} — AWI Client

This is a client workspace managed by AWI.
All vault rules, structure, taxonomy, and commands are in the parent AWI repo.

## Structure

- **Agenda:** `agenda/` — tasks, projects, people, daily, weekly
- **Documentation:** `documentation/` — writing style, business profile, wiki
- **Codebase:** `codebase/` — app submodules

## Get current date

Run from the AWI repo root:
```bash
bash .claude/hooks/get-datetime.sh full
```
"""

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


def init_client(name: str, parent_path: Path):
    path = (parent_path / name).resolve()

    if path.exists():
        print(f"Error: {path} already exists.")
        return None

    # Create agenda/ subfolders
    for folder in AGENDA_FOLDERS:
        (path / "agenda" / folder).mkdir(parents=True, exist_ok=True)

    # Agenda context files
    (path / "agenda" / ".abstract.md").write_text(AGENDA_ABSTRACT)
    (path / "agenda" / ".overview.md").write_text(AGENDA_OVERVIEW)

    # Create documentation/
    (path / "documentation").mkdir(parents=True, exist_ok=True)
    (path / "documentation" / ".abstract.md").write_text(DOCUMENTATION_ABSTRACT)

    # Create codebase/
    (path / "codebase").mkdir(parents=True, exist_ok=True)

    # Root files
    name_title = name.replace("-", " ").title()
    (path / "CLAUDE.md").write_text(CLAUDE_MD.format(name_title=name_title))
    (path / ".gitignore").write_text(GITIGNORE)

    # Initialize git
    subprocess.run(["git", "init"], cwd=path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"cos: initialize {name} client"],
        cwd=path,
        check=True,
    )

    print(f"Initialized {name} at {path}")
    print()
    print("Structure:")
    print(f"  agenda/        ← {', '.join(AGENDA_FOLDERS[:4])}, ...")
    print(f"  documentation/ ← writing style, business profile, wiki")
    print(f"  codebase/      ← app submodules go here")

    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold an AWI client repo")
    parser.add_argument("name", help="Client name slug (e.g. newhaze, afin, acme-corp)")
    parser.add_argument("path", nargs="?", default="_data/entities", help="Parent directory (default: _data/entities/)")
    args = parser.parse_args()

    init_client(args.name, Path(args.path))
