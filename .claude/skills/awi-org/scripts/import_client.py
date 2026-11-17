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

# Las constantes son las de `scaffold`: una org importada tiene que quedar con la
# misma estructura que una nueva. Tenía su propia copia, y era la que se iba a
# quedar atrás la próxima vez que cambiara el canon (ADR 0027).
from scaffold import (
    AGENDA_ABSTRACT,
    AGENDA_FOLDERS,
    AGENDA_OVERVIEW,
    CLAUDE_MD,
    DOCUMENTATION_ABSTRACT,
    DOCUMENTATION_OVERVIEW,
)


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
        agenda_abstract.write_text(AGENDA_ABSTRACT, encoding="utf-8")
        created.append(str(agenda_abstract.relative_to(path)))

    agenda_overview = path / "agenda" / ".overview.md"
    if not agenda_overview.exists():
        agenda_overview.write_text(AGENDA_OVERVIEW, encoding="utf-8")
        created.append(str(agenda_overview.relative_to(path)))

    # documentation/
    doc_dir = path / "documentation"
    if not doc_dir.exists():
        doc_dir.mkdir(parents=True, exist_ok=True)
        created.append("documentation/")

    for nombre, contenido in ((".abstract.md", DOCUMENTATION_ABSTRACT),
                              (".overview.md", DOCUMENTATION_OVERVIEW)):
        archivo = path / "documentation" / nombre
        if not archivo.exists():
            archivo.write_text(contenido, encoding="utf-8")
            created.append(str(archivo.relative_to(path)))

    # codebase/
    codebase = path / "codebase"
    if not codebase.exists():
        codebase.mkdir(parents=True, exist_ok=True)
        created.append("codebase/")

    # CLAUDE.md
    claude_md = path / "CLAUDE.md"
    if not claude_md.exists():
        claude_md.write_text(CLAUDE_MD.format(titulo=name.replace("-", " ").title()), encoding="utf-8")
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
        print(f"Error: {client_path} does not exist. Run /awi-initialize first.")
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
        ["git", "commit", "-m", f"chore({args.name}): add missing AWI structure"],
        cwd=client_path,
        check=True,
    )
    print(f"\nCommitted additions to {args.name}.")


if __name__ == "__main__":
    main()
