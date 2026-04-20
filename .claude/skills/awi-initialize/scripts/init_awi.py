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
Use /new-client <name> to add a client.
"""

CLAUDE_MD = """\
# Agentic Workflow Integrator (AWI) — Claude Code

**All vault rules, structure, taxonomy, and commands are in [INSTRUCTIONS.md](_system/agentic-workflow-integrator/INSTRUCTIONS.md).** Read it before any vault operation.

> **Do NOT modify this file for vault rules.** Update `_system/agentic-workflow-integrator/INSTRUCTIONS.md` instead — it is the single source of truth shared across all AI agents.

## Claude Code-specific

- PostToolUse hook auto-commits after Write/Edit operations on `_clients/` and `_system/` — do NOT commit manually unless asked.
- Skills available: `/awi-introduction`, `/awi-initialize`, `/new-client`, `/awi-user-create`, `/awi-user-login`, `/today`, `/week`, `/new`, `/history`, `/delegate`.
- Get current date: `bash .claude/hooks/get-datetime.sh full`.
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

INSTRUCTIONS_STUB = """\
# Agentic Workflow Integrator (AWI)

A system factory. AWI is the engine — it holds the operator's `_system/` (framework docs, users) and scaffolds `_clients/<name>/` entries for personal and company contexts. Each client follows the same `agenda/` + `documentation/` + `codebase/` structure.

Always run `bash .claude/hooks/get-datetime.sh full` to get the current date and time.

## Structure

```
awi/
  .claude/                     - Claude Code config: skills, hooks, reference, settings
  _system/                     - AWI framework (public) + vault users (private)
    agentic-workflow-integrator/
      INSTRUCTIONS.md          - This file — single source of truth
    users/                     - Vault user profiles (<username>.md)
    chief-of-staff/
      references/
        file-formats.md        - Full file format templates
  _clients/                    - One submodule per company/person
    <name>/
      agenda/                  - Tasks, projects, people, daily, outputs, etc.
      documentation/           - Writing style, business profile, wiki
      codebase/                - App repos (submodules)
```

Each `_clients/<name>/` is a **separate git repo** registered as a submodule of AWI.

Use `/new-client <name>` to scaffold a new client repo and register it.
"""


def init_awi(path: Path = Path(".")):
    path = path.resolve()

    # Create _system dirs
    for d in SYSTEM_DIRS:
        (path / d).mkdir(parents=True, exist_ok=True)

    # Write INSTRUCTIONS.md stub
    instructions_path = path / "_system" / "agentic-workflow-integrator" / "INSTRUCTIONS.md"
    if not instructions_path.exists():
        instructions_path.write_text(INSTRUCTIONS_STUB)

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
        ["git", "commit", "-m", "cos: initialize AWI repo"],
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
    print("  1. /new-client <name>")
    print("  2. /awi-user-create <username>")


if __name__ == "__main__":
    init_awi()
