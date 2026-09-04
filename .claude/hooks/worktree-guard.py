#!/usr/bin/env python3
"""PreToolUse: evita que dos sesiones se roben el checkout principal de un repo.

El modo de falla que cierra este hook (2026-09-04, newhaze-webapp): dos
sesiones el mismo día sobre el mismo checkout. Una estaba a mitad de un fix; la
otra hizo `git checkout` de otra rama. La primera siguió trabajando sin
enterarse, commiteó sobre la base equivocada y el PR salió colgando de la rama
ajena — se descubrió recién al mirar `git log` por otra razón.

No alcanza con documentarlo (`docs/agents/worktrees-paralelos.md` ya lo
explicaba cuando pasó, escrito unas horas antes). Cambiar de rama en un
checkout que otra sesión tiene tomado tiene que fallar, no depender de que
alguien se acuerde.

Sólo se mete con el **checkout principal** de un codebase de AWI, y sólo con
comandos que mueven `HEAD` de rama. Dentro de un worktree no dice nada: para
eso existen.

Protocolo: exit 2 = bloquear (stderr vuelve al agente). Cualquier otra falla
sale en silencio con 0 — romper la sesión es peor que no vigilar.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

SHARED = Path(__file__).resolve().parents[1] / "skills" / "shared" / "scripts"
sys.path.insert(0, str(SHARED))

try:
    from worktree import claim, is_worktree, lease_holder, main_checkout, repo_root
except ImportError:
    sys.exit(0)

# `git checkout <rama>` / `git switch <rama>` mueven HEAD. Quedan afuera las
# formas que tocan archivos y no la rama: `git checkout -- src/`,
# `git checkout origin/stg -- file`, `git switch --detach` sobre un sha.
SWITCH_RE = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?(checkout|switch)\b")
PATHSPEC_RE = re.compile(r"\s--\s")

# `cd <dir> && …` al principio del comando: es como trabaja el agente cuando el
# repo no es el cwd de la sesión.
CD_RE = re.compile(r"^\s*cd\s+(?P<dir>(?:\"[^\"]+\")|(?:'[^']+')|(?:[^\s;&|]+))")


def target_dir(command: str, cwd: str) -> Path:
    match = CD_RE.match(command)
    if match:
        raw = match.group("dir").strip("\"'")
        candidate = Path(raw).expanduser()
        if not candidate.is_absolute():
            candidate = Path(cwd) / candidate
        if candidate.is_dir():
            return candidate
    return Path(cwd)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    command = payload.get("tool_input", {}).get("command", "")
    if not command or not SWITCH_RE.search(command) or PATHSPEC_RE.search(command):
        return 0

    session_id = payload.get("session_id", "")
    directorio = target_dir(command, payload.get("cwd", "."))
    if not directorio.is_dir():
        return 0

    raiz = repo_root(directorio)
    if not raiz:
        return 0

    # El vault mismo no entra: acá no hay trabajo de código en paralelo, y
    # bloquear su checkout rompería las skills que sí lo tocan.
    if not any(part == "codebase" for part in raiz.parts):
        return 0

    if is_worktree(raiz):
        return 0

    principal = main_checkout(raiz)
    lease = lease_holder(principal)

    if lease and lease.get("session_id") not in ("", session_id):
        rama = lease.get("branch", "?")
        print(
            f"Otra sesión está trabajando en el checkout principal de {principal.name} "
            f"(rama «{rama}»). Cambiar de rama acá le reescribe los archivos abajo de "
            f"los pies y hace que commitee sobre la base equivocada.\n\n"
            f"Pedí tu propio worktree:\n"
            f"  python3 .claude/skills/shared/scripts/worktree.py provision "
            f"{principal.name} <tu-rama>\n\n"
            f"Si sabés que esa sesión terminó:\n"
            f"  python3 .claude/skills/shared/scripts/worktree.py release {principal.name}",
            file=sys.stderr,
        )
        return 2

    # Nadie lo tenía: esta sesión pasa a ser la dueña, y la próxima que llegue
    # verá el lease en vez de pisarla.
    claim(principal, session_id)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Un guard que rompe la sesión es peor que un guard que no mira.
        sys.exit(0)
