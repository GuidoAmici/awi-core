#!/usr/bin/env python3
"""Mecánica del ciclo de contexto compartido: traer, mirar, publicar.

Reemplaza a `/awi-sync`, que nació para reapuntar submódulos —cosa que ya no
existe— y cuyo resto de comportamiento era peligroso con varios operadores:
hacía `git add -A` y commiteaba todo con el mensaje fijo
`"chore(sync): stage local changes"`, y ante un rebase fallido marcaba `failed`,
retornaba y seguía con el próximo repo **sin abortar el rebase** — dejando el
repo a mitad de una operación que hay que sacar con comandos de git.

Este script es sólo la mecánica. El juicio —cuándo traer, cuándo sugerir
publicar, cómo se llama cada commit, si hay que preguntar— vive en
INSTRUCTIONS.md. La razón es empírica: `log_command` se invoca por instrucción en
22 archivos SKILL.md y el registro subcuenta, así que sabemos que las
instrucciones se cumplen a veces. Para un log alcanza; para traer el contexto de
otro operador, no. Ver ADR 0014 y 0015.

Alcance: los repos de **contexto** — orgs, sus codebases y el repo del propio
operador. Los repos marcados `upstream` quedan afuera: son dependencias, no
contexto, y su política es otra (ADR 0012).

Uso:
    python3 context_sync.py pull
    python3 context_sync.py status
    python3 context_sync.py push --repo <nombre> --message "<mensaje>"

Códigos de salida:
    0  todo bien
    1  error de configuración o de git
    3  se completó, pero algún repo necesita atención humana
"""

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manifest import Repo, plan
from paths import AWI_ROOT

NEEDS_ATTENTION = 3


@dataclass
class Result:
    repo: str
    state: str          # pulled · al-día · conflicto · sin-clonar · error
    detail: str = ""
    dirty: int = 0
    ahead: int = 0


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)


def context_repos() -> list[Repo]:
    """Repos de contexto, sin los upstream.

    Un repo `upstream` es una dependencia —comportamiento que se ejecuta— y no
    contexto —datos sobre los que se trabaja. Mezclarlos fue el error que el
    ADR 0012 corrige.
    """
    repos, warnings = plan(AWI_ROOT)
    for w in warnings:
        print(f"  ⚠ {w}", file=sys.stderr)
    return [r for r in repos if not r.upstream]


def dirty_count(path: Path) -> int:
    raw = git(path, "status", "--porcelain").stdout
    return len([ln for ln in raw.splitlines() if ln.strip()])


def ahead_count(path: Path, branch: str) -> int:
    r = git(path, "rev-list", "--count", f"origin/{branch}..HEAD")
    return int(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip().isdigit() else 0


def pull_one(r: Repo) -> Result:
    """Traer un repo sin dejarlo nunca a mitad de un rebase.

    `--autostash` deja trabajar con el árbol sucio, que es el estado normal al
    abrir una sesión. Si el rebase falla, se aborta y el repo vuelve a como
    estaba: preferimos reportar que un repo necesita atención antes que dejarlo
    en un estado del que hay que salir con comandos de git.
    """
    if not (r.path / ".git").exists():
        return Result(r.name, "sin-clonar", "corré /awi-initialize")

    if git(r.path, "fetch", "origin", "--quiet").returncode != 0:
        return Result(r.name, "error", "no se pudo contactar el remoto")

    before = git(r.path, "rev-parse", "HEAD").stdout.strip()
    res = git(r.path, "pull", "--rebase", "--autostash", "origin", r.branch)

    if res.returncode != 0:
        git(r.path, "rebase", "--abort")
        return Result(
            r.name, "conflicto",
            "tus cambios y los de otra persona tocan lo mismo; el repo quedó como estaba",
            dirty=dirty_count(r.path), ahead=ahead_count(r.path, r.branch),
        )

    after = git(r.path, "rev-parse", "HEAD").stdout.strip()
    state = "pulled" if before != after else "al-día"
    return Result(r.name, state, dirty=dirty_count(r.path), ahead=ahead_count(r.path, r.branch))


def push_one(r: Repo, message: str) -> Result:
    """Commitear lo que haya y publicarlo, con el mensaje que decidió la IA.

    El mensaje llega por parámetro a propósito. `/awi-sync` usaba una constante,
    y el resultado fue un historial compartido que es una pared de líneas
    idénticas — inútil para saber qué cambió y para generar un changelog.
    """
    if not (r.path / ".git").exists():
        return Result(r.name, "sin-clonar")

    if dirty_count(r.path):
        git(r.path, "add", "-A")
        res = git(r.path, "commit", "-m", message)
        if res.returncode != 0 and "nothing to commit" not in (res.stdout + res.stderr):
            return Result(r.name, "error", f"commit falló: {res.stderr.strip()}")

    if ahead_count(r.path, r.branch) == 0:
        return Result(r.name, "al-día", "nada para publicar")

    res = git(r.path, "push", "origin", r.branch)
    if res.returncode != 0:
        return Result(
            r.name, "conflicto",
            "el remoto tiene cambios que no tenés; traé primero (pull) y volvé a intentar",
        )
    return Result(r.name, "publicado")


def report(results: list[Result], header: str) -> int:
    icons = {"pulled": "↓", "publicado": "↑", "al-día": "·", "conflicto": "⚠", "sin-clonar": "○", "error": "✗"}
    print(f"\n{header}")
    attention = []
    for res in sorted(results, key=lambda x: (x.state != "conflicto", x.repo)):
        line = f"  {icons.get(res.state, '?')} {res.repo:28} {res.state}"
        if res.dirty:
            line += f"  ({res.dirty} sin commitear)"
        print(line)
        if res.detail:
            print(f"      {res.detail}")
        if res.state in ("conflicto", "error"):
            attention.append(res.repo)

    if attention:
        print(f"\n  {len(attention)} repo(s) necesitan atención: {', '.join(attention)}")
        print("  Ningún repo quedó a medias — todos están en un estado del que se puede seguir.")
        return NEEDS_ATTENTION
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description="Ciclo de contexto compartido")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pull", help="Traer los cambios de todos los repos de contexto")
    sub.add_parser("status", help="Qué hay sin commitear y sin publicar, por repo")
    p = sub.add_parser("push", help="Commitear y publicar un repo")
    p.add_argument("--repo", required=True, help="Nombre del repo, como aparece en pull/status")
    p.add_argument("--message", required=True, help="Mensaje de commit (Conventional Commits)")
    args = ap.parse_args()

    repos = context_repos()
    if not repos:
        print("No hay repos de contexto materializados.")
        return

    if args.cmd == "pull":
        sys.exit(report([pull_one(r) for r in repos], "Contexto compartido — traído:"))

    if args.cmd == "status":
        results = [
            Result(r.name, "al-día" if (r.path / ".git").exists() else "sin-clonar",
                   dirty=dirty_count(r.path) if (r.path / ".git").exists() else 0,
                   ahead=ahead_count(r.path, r.branch) if (r.path / ".git").exists() else 0)
            for r in repos
        ]
        pending = [x for x in results if x.dirty or x.ahead]
        if not pending:
            print("Todo publicado — no hay nada sin commitear ni sin subir.")
            return
        print("\nSin publicar:")
        for x in pending:
            bits = []
            if x.dirty:
                bits.append(f"{x.dirty} archivo(s) sin commitear")
            if x.ahead:
                bits.append(f"{x.ahead} commit(s) sin subir")
            print(f"  · {x.repo:28} {', '.join(bits)}")
        return

    match = [r for r in repos if r.name == args.repo]
    if not match:
        print(f"✗ '{args.repo}' no es un repo de contexto. Opciones: {', '.join(r.name for r in repos)}",
              file=sys.stderr)
        sys.exit(1)
    sys.exit(report([push_one(match[0], args.message)], f"Publicando {args.repo}:"))


if __name__ == "__main__":
    main()
