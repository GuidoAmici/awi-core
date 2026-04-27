#!/usr/bin/env python3
"""
Scaffold missing AWI structure into an existing client repo.

Checks for required folders/files under _data/organizations/<name>/ and creates
only what is absent — never overwrites existing content.

Usage:
    python3 import_client.py <name> [<parent_path>]
"""

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared" / "scripts"))
from paths import ORGANIZATIONS_RELDIR

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

DOCUMENTATION_ABSTRACT = "Context files: writing style, business profile, documentation.\n"

CLAUDE_MD = """\
# {name_title} — AWI Client

This is a client workspace managed by AWI.
All vault rules, structure, taxonomy, and commands are in the parent AWI repo.

## Structure

- **Agenda:** `agenda/` — tasks, projects, people, daily, weekly
- **Documentation:** `documentation/` — writing style, business profile, context
- **Codebase:** `codebase/` — app submodules

## Get current date

Run from the AWI repo root:
```bash
bash .claude/hooks/get-datetime.sh full
```
"""


def scaffold_missing(path: Path, name: str) -> list[str]:
    """Create missing AWI structure. Returns list of created paths."""
    created = []

    # agenda/ subfolders
    for folder in AGENDA_FOLDERS:
        d = path / "agenda" / folder
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            created.append(str(d.relative_to(path)))

    # agenda context files
    agenda_abstract = path / "agenda" / ".abstract.md"
    if not agenda_abstract.exists():
        agenda_abstract.write_text(AGENDA_ABSTRACT)
        created.append(str(agenda_abstract.relative_to(path)))

    agenda_overview = path / "agenda" / ".overview.md"
    if not agenda_overview.exists():
        agenda_overview.write_text(AGENDA_OVERVIEW)
        created.append(str(agenda_overview.relative_to(path)))

    # documentation/
    doc_dir = path / "documentation"
    if not doc_dir.exists():
        doc_dir.mkdir(parents=True, exist_ok=True)
        created.append("documentation/")

    doc_abstract = path / "documentation" / ".abstract.md"
    if not doc_abstract.exists():
        doc_abstract.write_text(DOCUMENTATION_ABSTRACT)
        created.append(str(doc_abstract.relative_to(path)))

    # codebase/
    codebase = path / "codebase"
    if not codebase.exists():
        codebase.mkdir(parents=True, exist_ok=True)
        created.append("codebase/")

    # CLAUDE.md
    claude_md = path / "CLAUDE.md"
    if not claude_md.exists():
        name_title = name.replace("-", " ").title()
        claude_md.write_text(CLAUDE_MD.format(name_title=name_title))
        created.append("CLAUDE.md")

    return created


def main():
    parser = argparse.ArgumentParser(description="Scaffold missing AWI structure into an imported client repo")
    parser.add_argument("name", help="Client slug (must already exist under parent_path/)")
    parser.add_argument("path", nargs="?", default=ORGANIZATIONS_RELDIR, help="Parent directory (default: _data/organizations/)")
    args = parser.parse_args()

    parent = Path(args.path).resolve()
    client_path = parent / args.name

    if not client_path.exists():
        print(f"Error: {client_path} does not exist. Run 'git submodule add' first.")
        raise SystemExit(1)

    created = scaffold_missing(client_path, args.name)

    if not created:
        print(f"{args.name}: AWI structure already complete — nothing to add.")
        return

    print(f"{args.name}: scaffolded {len(created)} missing items:")
    for item in created:
        print(f"  + {item}")

    # Commit additions
    subprocess.run(["git", "add", "-A"], cwd=client_path, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"cos: add missing AWI structure to {args.name}"],
        cwd=client_path,
        check=True,
    )
    print(f"\nCommitted additions to {args.name}.")


if __name__ == "__main__":
    main()
