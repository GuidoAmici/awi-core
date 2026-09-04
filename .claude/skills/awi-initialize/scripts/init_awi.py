#!/usr/bin/env python3
"""Bootstrap a fresh AWI repo structure."""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared" / "scripts"))
from paths import (
    USERS_RELDIR,
    SYSTEM_AWI_RELDIR,
    SYSTEM_COS_REFS_RELDIR,
    SYSTEM_GTD_RELDIR,
)

SYSTEM_DIRS = [
    USERS_RELDIR,
    SYSTEM_COS_REFS_RELDIR,
    SYSTEM_GTD_RELDIR,
    SYSTEM_AWI_RELDIR,
]

CLIENTS_ABSTRACT = """\
One submodule per company or personal context.
Each client has agenda/, documentation/, and codebase/.
Use /awi-org <name> to add an organization.
"""

CLAUDE_MD = """\
# AWI — Agentic Workflow Integrator

Este archivo es la fuente de verdad de las reglas de esta instancia. La forma de la
respuesta la trae el plugin `answerable`, instalado aparte.

## Siempre

- **La fecha se pregunta, no se supone:** `bash .claude/hooks/get-datetime.sh full`.
- **Los comandos que ejecutás vos llevan rutas relativas** desde la raíz del proyecto.
- **Commiteá en los cortes lógicos de la tarea**, en Conventional Commits con scope.
  No hay hook de auto-commit: no dejes trabajo terminado sin commitear, ni commitees
  después de cada `Write`.

## Estructura

Cada `_data/organizations/<name>/` y cada `_data/users/<github-id>/` es un repo de git
aparte, declarado en `user-submodules.json` y materializado por `git clone`. Nada en AWI
es un submódulo. `_data/` está en `.gitignore` por corrección: sin eso un `git add -A`
en la raíz se traga los hijos como repos embebidos.

## Skills

`/awi-introduction`, `/awi-initialize`, `/awi-org`, `/awi-user`, `/today`, `/week`,
`/new`, `/history`, `/triage`, `/delegate-issue`, `/wrap-session`.
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

def init_awi(path: Path = Path(".")):
    path = path.resolve()

    # Create _system dirs
    for d in SYSTEM_DIRS:
        (path / d).mkdir(parents=True, exist_ok=True)

    # Create _clients/
    clients_path = path / "_clients"
    clients_path.mkdir(exist_ok=True)
    (clients_path / ".abstract.md").write_text(CLIENTS_ABSTRACT)

    # Create root files
    (path / "CLAUDE.md").write_text(CLAUDE_MD)
    (path / ".gitignore").write_text(GITIGNORE)

    # Init git
    subprocess.run(["git", "init"], cwd=path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: initialize AWI repo"],
        cwd=path,
        check=True,
    )

    print(f"AWI initialized at {path}")
    print()
    print("Structure:")
    print("  _system/     ← framework docs, user profiles")
    print("  _clients/    ← client repos go here (one submodule each)")
    print()
    print("Next steps:")
    print("  1. /awi-org <name>")
    print("  2. /awi-user-create <username>")


if __name__ == "__main__":
    init_awi()
