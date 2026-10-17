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
    python3 worktree.py sweep [--dry-run]
"""

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
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


# ── Barrido de worktrees terminados ───────────────────────────────────────────
#
# Cada worktree es una copia entera del repo, y nadie los borra: el 2026-10-17
# había 106 worktrees y ~10 GB en los cuatro codebases, la mayoría de ramas ya
# mergeadas. Ese disco es parte de lo que dejó C: en 0 bytes esa noche.
#
# Se borra sólo lo que no puede perder nada: el PR de la rama ya se cerró hace
# más de SWEEP_GRACE_HOURS, no hay cambios sin commitear y cada commit del
# worktree está también en el remoto. Ante cualquier duda, el worktree queda.

SWEEP_GRACE_HOURS = 2

# Lo que `provision` agrega y git no conoce. No es trabajo sin guardar: se
# borra antes de soltar el worktree, para que `git worktree remove` lo acepte.
PROVISIONED_FILES = {PORT_FILE, *LINKED_IGNORED_FILES}


def prs_by_branch(repo: Path) -> dict[str, dict] | None:
    """Último PR de cada rama, o None si `gh` no responde para este repo."""
    try:
        rc = subprocess.run(
            ["gh", "pr", "list", "--state", "all", "--limit", "1000",
             "--json", "number,headRefName,headRefOid,state,closedAt"],
            cwd=repo, capture_output=True, text=True, timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    if rc.returncode != 0:
        return None
    mapa: dict[str, dict] = {}
    for pr in json.loads(rc.stdout or "[]"):
        previo = mapa.get(pr["headRefName"])
        # Un PR abierto manda: la rama sigue viva aunque tenga uno viejo cerrado.
        if previo is None or pr["state"] == "OPEN" or (
            previo["state"] != "OPEN" and pr["number"] > previo["number"]
        ):
            mapa[pr["headRefName"]] = pr
    return mapa


def secondary_worktrees(principal: Path) -> list[dict]:
    """Worktrees bajo `.claude/worktrees/` del repo, con su rama y su HEAD."""
    rc = git(["worktree", "list", "--porcelain"], cwd=principal)
    raiz = (principal / WORKTREES_SUBDIR).resolve()
    encontrados, actual = [], {}
    for linea in rc.stdout.splitlines() + [""]:
        if not linea:
            if actual.get("path") and actual["path"].resolve().parent == raiz:
                encontrados.append(actual)
            actual = {}
        elif linea.startswith("worktree "):
            actual["path"] = Path(linea.split(" ", 1)[1])
        elif linea.startswith("HEAD "):
            actual["head"] = linea.split(" ", 1)[1]
        elif linea.startswith("branch refs/heads/"):
            actual["branch"] = linea.removeprefix("branch refs/heads/")
    return encontrados


def processes_inside(path: Path) -> list[str]:
    """Procesos cuyo directorio de trabajo está dentro de `path`."""
    raiz = str(path.resolve())
    nombres = []
    for proc in Path("/proc").glob("[0-9]*"):
        try:
            cwd = os.readlink(proc / "cwd")
        except OSError:
            continue
        if cwd == raiz or cwd.startswith(raiz + "/"):
            try:
                nombres.append((proc / "comm").read_text().strip())
            except OSError:
                nombres.append(proc.name)
    return nombres


def unsaved_work(worktree: Path) -> str | None:
    rc = git(["status", "--porcelain", "--untracked-files=all"], cwd=worktree)
    if rc.returncode != 0:
        return "git status falló"
    pendientes = [l for l in rc.stdout.splitlines() if l[3:].strip() not in PROVISIONED_FILES]
    return f"{len(pendientes)} archivo(s) sin commitear" if pendientes else None


def only_local_commits(worktree: Path, head: str, pr: dict) -> bool:
    """True si HEAD tiene commits que no están en ningún lado más que acá."""
    if head == pr.get("headRefOid"):
        return False
    rc = git(["branch", "-r", "--contains", head], cwd=worktree)
    return not rc.stdout.strip()


def hours_since(iso: str | None) -> float:
    if not iso:
        return 0.0
    cerrado = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - cerrado).total_seconds() / 3600


def sweep_verdict(wt: dict, pr: dict | None) -> str | None:
    """Motivo para conservar el worktree, o None si se puede borrar."""
    if not wt.get("branch"):
        return "con HEAD suelto"
    if pr is None:
        return "sin PR"
    if pr["state"] == "OPEN":
        return "con PR abierto"
    if hours_since(pr.get("closedAt")) < SWEEP_GRACE_HOURS:
        return f"con PR cerrado hace menos de {SWEEP_GRACE_HOURS} h"
    if unsaved_work(wt["path"]):
        return "con cambios sin commitear"
    if only_local_commits(wt["path"], wt.get("head", ""), pr):
        return "con commits que no están en el remoto"
    if processes_inside(wt["path"]):
        return "en uso por un proceso"
    return None


def remove_worktree(principal: Path, wt: dict, pr: dict) -> str | None:
    """Borra el worktree; devuelve el error, o None si salió bien."""
    for nombre in PROVISIONED_FILES:
        extra = wt["path"] / nombre
        # Hubo ramas que commitearon `.worktree-port`: borrarlo ahí sería un
        # cambio, y `git worktree remove` lo rechaza con razón.
        versionado = git(["ls-files", "--error-unmatch", nombre], cwd=wt["path"]).returncode == 0
        if not versionado and (extra.is_symlink() or extra.is_file()):
            extra.unlink()
    rc = git(["worktree", "remove", str(wt["path"])], cwd=principal)
    if rc.returncode != 0:
        return rc.stderr.strip().splitlines()[-1] if rc.stderr.strip() else "git worktree remove falló"
    # La rama local se va sólo si todo lo suyo entró por el merge. Un PR cerrado
    # sin mergear conserva la rama: es lo único que queda de ese trabajo.
    if pr["state"] == "MERGED" and wt.get("head") == pr.get("headRefOid"):
        git(["branch", "-D", wt["branch"]], cwd=principal)
    return None


def cmd_sweep(dry_run: bool) -> int:
    borrados, conservados, errores = [], {}, []
    for nombre, repo in sorted(all_codebases().items()):
        if "/" in nombre:
            continue
        principal = main_checkout(repo)
        git(["worktree", "prune"], cwd=principal)
        worktrees = secondary_worktrees(principal)
        if not worktrees:
            continue
        prs = prs_by_branch(principal)
        if prs is None:
            conservados["sin respuesta de gh"] = conservados.get("sin respuesta de gh", 0) + len(worktrees)
            continue
        for wt in worktrees:
            pr = prs.get(wt.get("branch", ""))
            if motivo := sweep_verdict(wt, pr):
                conservados[motivo] = conservados.get(motivo, 0) + 1
                continue
            etiqueta = f"{nombre}/{wt['path'].name} (PR #{pr['number']} {pr['state'].lower()})"
            if dry_run:
                borrados.append(etiqueta)
            elif error := remove_worktree(principal, wt, pr):
                errores.append(f"{etiqueta}: {error}")
            else:
                borrados.append(etiqueta)

    verbo = "Se borrarían" if dry_run else "Borrados"
    if borrados:
        print(f"{verbo} {len(borrados)} worktree(s) de ramas terminadas:")
        print("\n".join(f"  {b}" for b in borrados))
    for e in errores:
        print(f"  no pude borrar {e}")
    if conservados and (dry_run or borrados or errores):
        resumen = ", ".join(f"{n} {m}" for m, n in sorted(conservados.items(), key=lambda x: -x[1]))
        print(f"Conservados: {resumen}")
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

    p = sub.add_parser("sweep", help="Borrar los worktrees de ramas cuyo PR ya se cerró")
    p.add_argument("--dry-run", action="store_true", help="Sólo listar lo que se borraría")

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
    if args.cmd == "sweep":
        return cmd_sweep(args.dry_run)
    return 1


if __name__ == "__main__":
    sys.exit(main())
