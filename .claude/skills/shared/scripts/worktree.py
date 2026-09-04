#!/usr/bin/env python3
"""Mecánica de worktrees: un directorio por rama, para que dos sesiones no se pisen.

Un working tree tiene un solo `HEAD`. Dos sesiones en el mismo checkout no se
molestan un poco: la de al lado te reescribe los archivos abajo de los pies, y
el modo de falla es silencioso — commiteás sobre la base equivocada y te
enterás cuando el PR trae los commits de otro. Pasó el 2026-09-04 en
newhaze-webapp, con dos sesiones el mismo día: una empezó un fix, la otra hizo
`git checkout` en el medio, y el commit terminó colgando de la rama ajena.

El aislamiento del worktree es del checkout, no de la máquina. Los cuatro
recursos que siguen compartidos están en `docs/agents/worktrees-paralelos.md`;
este script se ocupa de los dos que puede automatizar (archivos ignorados y
puerto del dev server) y deja anotados los otros dos.

Uso:
    python3 worktree.py provision <codebase> <rama> [--base stg] [--sin-install]
    python3 worktree.py list
    python3 worktree.py status [<codebase>]
    python3 worktree.py release <codebase>
"""

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

from paths import AWI_ROOT, ORGANIZATIONS_DIR

# El lease no se versiona: es estado de esta máquina. `.claude/tmp/` ya está en
# .gitignore por la misma razón.
LEASE_FILE = AWI_ROOT / ".claude" / "tmp" / "checkout-leases.json"

# Un lease viejo no bloquea a nadie: una sesión que se murió sin soltar el
# checkout no puede dejarlo inutilizable para siempre.
LEASE_TTL_SECONDS = 8 * 3600

# Archivos que el repo ignora pero la app necesita. Se symlinkean, no se
# copian: un secreto rotado en el checkout principal tiene que valer para
# todos los worktrees sin volver a provisionar.
LINKED_IGNORED_FILES = [".env", ".env.local", ".env.development.local", ".env.test.local"]

WORKTREES_SUBDIR = Path(".claude") / "worktrees"
PORT_FILE = ".worktree-port"
PORT_RANGE_START = 3000


def git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)


# ── Resolución de codebases ───────────────────────────────────────────────────

def all_codebases() -> dict[str, Path]:
    """Todos los codebases montados, por nombre. `<org>/<codebase>` desambigua."""
    found: dict[str, Path] = {}
    if not ORGANIZATIONS_DIR.exists():
        return found
    for org in sorted(ORGANIZATIONS_DIR.iterdir()):
        codebase_dir = org / "codebase"
        if not codebase_dir.is_dir():
            continue
        for repo in sorted(codebase_dir.iterdir()):
            if (repo / ".git").exists():
                found[repo.name] = repo
                found[f"{org.name}/{repo.name}"] = repo
    return found


def resolve_codebase(ref: str) -> Path:
    """Nombre (`newhaze-webapp`), `<org>/<nombre>` o ruta."""
    candidate = Path(ref).expanduser()
    if (candidate / ".git").exists():
        return candidate.resolve()
    known = all_codebases()
    if ref in known:
        return known[ref]
    nombres = sorted({p.name for p in known.values()})
    sys.exit(f"No encuentro el codebase «{ref}». Montados: {', '.join(nombres) or 'ninguno'}")


def repo_root(path: Path) -> Path | None:
    """Raíz del working tree que contiene `path`, o None si no es un repo."""
    rc = git(["rev-parse", "--show-toplevel"], cwd=path)
    return Path(rc.stdout.strip()) if rc.returncode == 0 and rc.stdout.strip() else None


def main_checkout(path: Path) -> Path:
    """Checkout principal del repo — el primero que lista `git worktree list`."""
    rc = git(["worktree", "list", "--porcelain"], cwd=path)
    for line in rc.stdout.splitlines():
        if line.startswith("worktree "):
            return Path(line.split(" ", 1)[1])
    return path


def is_worktree(path: Path) -> bool:
    """True si `path` es un worktree secundario, no el checkout principal."""
    root = repo_root(path)
    return bool(root) and root.resolve() != main_checkout(path).resolve()


def current_branch(path: Path) -> str:
    rc = git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=path)
    return rc.stdout.strip() or "?"


# ── Lease del checkout principal ──────────────────────────────────────────────

def load_leases() -> dict:
    if not LEASE_FILE.exists():
        return {}
    try:
        return json.loads(LEASE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_leases(leases: dict) -> None:
    LEASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    LEASE_FILE.write_text(json.dumps(leases, indent=2, ensure_ascii=False) + "\n")


def lease_holder(checkout: Path) -> dict | None:
    """Lease vigente sobre ese checkout, o None si no hay o ya venció."""
    lease = load_leases().get(str(checkout))
    if not lease:
        return None
    if time.time() - lease.get("ts", 0) > LEASE_TTL_SECONDS:
        return None
    return lease


def claim(checkout: Path, session_id: str) -> None:
    leases = load_leases()
    leases[str(checkout)] = {
        "session_id": session_id,
        "ts": time.time(),
        "branch": current_branch(checkout),
    }
    save_leases(leases)


def release(checkout: Path) -> bool:
    leases = load_leases()
    if str(checkout) in leases:
        del leases[str(checkout)]
        save_leases(leases)
        return True
    return False


# ── Provisión ─────────────────────────────────────────────────────────────────

def slugify(branch: str) -> str:
    """`feat/195-carrito` → `195-carrito`: el directorio no anida por la barra."""
    return branch.split("/")[-1] or branch.replace("/", "-")


def port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("127.0.0.1", port)) == 0


def taken_ports(repo: Path) -> set[int]:
    """Puertos ya asignados a otros worktrees de este repo."""
    ports = set()
    for candidate in [repo, *(repo / WORKTREES_SUBDIR).glob("*")]:
        marker = candidate / PORT_FILE
        if marker.is_file():
            try:
                ports.add(int(marker.read_text().strip()))
            except ValueError:
                pass
    return ports


def assign_port(repo: Path, worktree: Path) -> int:
    """Puerto propio. El compartido no falla: hace que testees la app de otro."""
    ocupados = taken_ports(repo)
    port = PORT_RANGE_START
    while port in ocupados or port_in_use(port):
        port += 1
    (worktree / PORT_FILE).write_text(f"{port}\n")
    return port


def link_ignored_files(source: Path, worktree: Path) -> list[str]:
    """Symlinks a los archivos que git ignora pero la app necesita."""
    linked = []
    for name in LINKED_IGNORED_FILES:
        origin = source / name
        target = worktree / name
        if origin.is_file() and not target.exists():
            os.symlink(origin, target)
            linked.append(name)
    return linked


def provision(codebase: str, branch: str, base: str | None, install: bool) -> int:
    repo = resolve_codebase(codebase)
    principal = main_checkout(repo)
    worktree = principal / WORKTREES_SUBDIR / slugify(branch)

    if worktree.exists():
        print(f"Ya existe: {worktree}")
        print(f"  rama: {current_branch(worktree)}")
        return 0

    existe_rama = git(["rev-parse", "--verify", branch], cwd=principal).returncode == 0
    if existe_rama:
        args = ["worktree", "add", str(worktree), branch]
    else:
        base_ref = base or "origin/stg"
        if git(["rev-parse", "--verify", base_ref], cwd=principal).returncode != 0:
            base_ref = "HEAD"
        args = ["worktree", "add", "-b", branch, str(worktree), base_ref]

    rc = git(args, cwd=principal)
    if rc.returncode != 0:
        print(f"No pude crear el worktree:\n{rc.stderr.strip()}", file=sys.stderr)
        return 1

    print(f"Worktree creado: {worktree}")
    print(f"  rama: {branch}" + ("" if existe_rama else f" (nueva, desde {args[-1]})"))

    enlazados = link_ignored_files(principal, worktree)
    if enlazados:
        print(f"  symlinks: {', '.join(enlazados)}")

    port = assign_port(principal, worktree)
    print(f"  puerto: {port} (en {PORT_FILE})")

    if install and (worktree / "package.json").is_file():
        print("  instalando dependencias…")
        rc = subprocess.run(["npm", "install"], cwd=worktree, capture_output=True, text=True)
        print("  dependencias: " + ("ok" if rc.returncode == 0 else f"falló — {rc.stderr.strip()[:200]}"))

    # El stack de base de datos no se aísla: es el cuarto recurso compartido y
    # no hay nada que este script pueda hacer por él.
    if (worktree / "supabase").is_dir():
        print("  ⚠ stack de base de datos compartido: serializá las migraciones entre worktrees")

    print(f"\nEntrá con:  cd {worktree}")
    return 0


# ── Reportes ──────────────────────────────────────────────────────────────────

def cmd_list() -> int:
    hay = False
    for nombre, repo in sorted(all_codebases().items()):
        if "/" in nombre:
            continue
        rc = git(["worktree", "list"], cwd=repo)
        lineas = [l for l in rc.stdout.splitlines() if l.strip()]
        if len(lineas) <= 1:
            continue
        hay = True
        print(f"{nombre}:")
        for linea in lineas:
            partes = linea.split()
            ruta = Path(partes[0])
            rama = partes[-1].strip("[]") if len(partes) > 2 else "?"
            marca = "principal" if ruta.resolve() == main_checkout(repo).resolve() else ruta.name
            print(f"  · {marca:<28} {rama}")
    if not hay:
        print("Ningún codebase tiene worktrees. Todo el trabajo comparte el checkout principal.")
    return 0


def cmd_status(codebase: str | None) -> int:
    objetivos = [resolve_codebase(codebase)] if codebase else [
        p for n, p in sorted(all_codebases().items()) if "/" not in n
    ]
    for repo in objetivos:
        principal = main_checkout(repo)
        lease = lease_holder(principal)
        estado = f"tomado por la sesión {lease['session_id'][:8]}" if lease else "libre"
        print(f"{principal.name}: {current_branch(principal)} — checkout principal {estado}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Worktrees de AWI: un directorio por rama.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("provision", help="Crear y equipar un worktree para una rama")
    p.add_argument("codebase")
    p.add_argument("branch")
    p.add_argument("--base", default=None, help="Ref desde la que sale la rama nueva (default: origin/stg)")
    p.add_argument("--sin-install", action="store_true", help="No correr npm install")

    sub.add_parser("list", help="Worktrees de todos los codebases montados")

    p = sub.add_parser("status", help="Quién tiene tomado cada checkout principal")
    p.add_argument("codebase", nargs="?")

    p = sub.add_parser("release", help="Soltar el lease del checkout principal")
    p.add_argument("codebase")

    args = parser.parse_args()

    if args.cmd == "provision":
        return provision(args.codebase, args.branch, args.base, not args.sin_install)
    if args.cmd == "list":
        return cmd_list()
    if args.cmd == "status":
        return cmd_status(args.codebase)
    if args.cmd == "release":
        checkout = main_checkout(resolve_codebase(args.codebase))
        print("Lease liberado." if release(checkout) else "No había lease.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
