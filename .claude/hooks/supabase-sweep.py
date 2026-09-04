#!/usr/bin/env python3
"""SessionStart: baja los stacks de Supabase que ya no le sirven a nadie.

Cada stack local son ~11 contenedores y ~1,7 GiB. Con un stack por worktree
—el camino natural cuando varios agentes trabajan en paralelo— alcanza con
que un par de sesiones mueran sin bajar el suyo para que la RAM de la máquina
se vaya en stacks que nadie está usando. El operador se entera cuando ya no
puede levantar nada.

Barrido al arranque, no limpieza al cierre: una sesión que se muere no ejecuta
su cleanup, así que la limpieza no puede depender de que el cierre sea limpio.
Reconciliar en el arranque cubre también los cierres sucios, que son
justamente los que dejan basura.

Dos criterios, deliberadamente conservadores — parar un stack que alguien está
usando es peor que dejar uno de más:

  huérfano   el project_id no corresponde a ningún supabase/config.toml
             montado en AWI. Nadie puede estar usándolo: se baja.
  inactivo   el proyecto existe, pero ningún checkout suyo tiene lease vigente
             y el stack lleva más de IDLE_HOURS arriba. Se baja.

Todo lo demás se deja en paz.

Protocolo: siempre exit 0. Un barrido que rompe el arranque de la sesión es
peor que un stack colgado.
"""

import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SHARED = Path(__file__).resolve().parents[1] / "skills" / "shared" / "scripts"
sys.path.insert(0, str(SHARED))

try:
    from worktree import LEASE_TTL_SECONDS, all_codebases, lease_holder, main_checkout
except ImportError:
    sys.exit(0)

# Un stack recién levantado nunca se toca, aunque no haya lease: el operador
# puede haberlo arrancado a mano hace un minuto para mirar algo.
IDLE_HOURS = LEASE_TTL_SECONDS / 3600

# Docker Desktop en Windows no siempre expone `docker` dentro de WSL.
DOCKER_FALLBACK = "/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"

# supabase_<servicio>_<project_id> — el CLI nombra así todo lo que levanta.
CONTAINER_RE = re.compile(r"^supabase_(?P<svc>[a-z_]+)_(?P<project>.+)$")
PROJECT_ID_RE = re.compile(r'^\s*project_id\s*=\s*"([^"]+)"', re.MULTILINE)


def docker_bin() -> str | None:
    found = shutil.which("docker")
    if found:
        return found
    return DOCKER_FALLBACK if Path(DOCKER_FALLBACK).exists() else None


def docker(binario: str, *args: str) -> str | None:
    """stdout del comando, o None si docker no responde (daemon abajo, timeout)."""
    try:
        rc = subprocess.run(
            [binario, *args], capture_output=True, text=True, timeout=8
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    return rc.stdout if rc.returncode == 0 else None


def proyectos_en_disco() -> dict[str, Path]:
    """project_id → checkout, para cada supabase/config.toml montado en AWI."""
    mapa: dict[str, Path] = {}
    for repo in set(all_codebases().values()):
        # El config.toml del checkout principal y el de cada worktree: un
        # worktree puede declarar su propio project_id para tener stack propio.
        for cfg in [repo / "supabase" / "config.toml", *repo.glob(".claude/worktrees/*/supabase/config.toml")]:
            try:
                match = PROJECT_ID_RE.search(cfg.read_text(encoding="utf-8"))
            except OSError:
                continue
            if match:
                # setdefault, no asignación: hoy los worktrees heredan el
                # config.toml versionado, así que comparten project_id. El
                # checkout principal va primero en la lista y debe ganar —
                # asociar el stack a un worktree cualquiera hace que el mapa
                # cambie según qué worktrees existan en ese momento.
                mapa.setdefault(match.group(1), cfg.parent.parent)
    return mapa


def horas_arriba(binario: str, contenedor: str) -> float:
    salida = docker(binario, "inspect", "--format", "{{.State.StartedAt}}", contenedor)
    if not salida:
        return 0.0
    try:
        inicio = datetime.fromisoformat(salida.strip().replace("Z", "+00:00"))
    except ValueError:
        return 0.0
    return (datetime.now(timezone.utc) - inicio).total_seconds() / 3600


def alguien_lo_usa(checkout: Path) -> bool:
    """¿Algún checkout de ese repo tiene lease vigente?"""
    try:
        principal = main_checkout(checkout)
    except Exception:
        return True  # ante la duda, no se toca
    return lease_holder(principal) is not None


def main() -> int:
    binario = docker_bin()
    if not binario:
        return 0

    salida = docker(binario, "ps", "--filter", "name=supabase_", "--format", "{{.Names}}")
    if not salida:
        return 0  # daemon abajo o sin contenedores: nada que barrer

    # Un project_id agrupa varios contenedores; basta un representante por stack.
    stacks: dict[str, str] = {}
    for nombre in salida.split():
        match = CONTAINER_RE.match(nombre)
        if match:
            stacks.setdefault(match.group("project"), nombre)
    if not stacks:
        return 0

    en_disco = proyectos_en_disco()
    bajados: list[str] = []

    for project_id, contenedor in sorted(stacks.items()):
        checkout = en_disco.get(project_id)
        if checkout is None:
            motivo = "huérfano — sin config.toml en AWI"
        elif alguien_lo_usa(checkout):
            continue
        elif horas_arriba(binario, contenedor) < IDLE_HOURS:
            continue
        else:
            motivo = f"inactivo — sin lease y +{IDLE_HOURS:.0f} h arriba"

        parados = docker(binario, "ps", "-q", "--filter", f"name=supabase_.*_{project_id}$")
        if parados is None:
            continue
        ids = parados.split()
        if ids and docker(binario, "stop", *ids) is not None:
            bajados.append(f"  {project_id} — {motivo}")

    if bajados:
        print("Stacks de Supabase bajados por el barrido de arranque:")
        print("\n".join(bajados))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)  # nunca romper el arranque de la sesión
