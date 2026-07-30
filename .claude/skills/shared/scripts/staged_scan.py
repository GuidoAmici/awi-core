"""Prevención: escanea el índice antes de que el material entre al historial.

Consume **el mismo motor y el mismo archivo de reglas** que `history_audit`. Ese
es el punto entero: si el hook tuviera su propia lista, divergiría de la
auditoría y dejaría pasar exactamente lo que la auditoría busca. Ver PRD 1
(issue #80), subissue #88.

Tres modos, uno por hook de git:

    --hook              pre-commit: escanea el índice y bloquea
    --registrar-salteo  post-commit: si el pre-commit no corrió, lo anota
    --instalar          apunta core.hooksPath a .claude/hooks/git

El salteo usa el mecanismo estándar de git (`git commit --no-verify`), que por
definición no ejecuta el hook — así que el propio hook no puede registrar su
salteo. Lo resuelve el par pre/post: el pre-commit deja la marca del árbol que
aprobó, y el post-commit compara. Si el commit trae un árbol que nadie aprobó,
fue salteado, y queda anotado.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import sensitive_scan as ss

#: Dónde viven los hooks de git de AWI. Versionados, así que llegan con el
#: harness: una instancia que hace /awi-update recibe la prevención.
HOOKS_RELDIR = ".claude/hooks/git"

#: Marca y registro viven en .git/, que nunca se versiona. Un registro de
#: salteos no puede ser algo que se filtre ni que se pierda en un pull.
MARCA = "awi-sensitive-scan-aprobado"
REGISTRO = "awi-sensitive-scan-salteos.log"

SALTEO = "git commit --no-verify"


class ErrorDeGit(RuntimeError):
    pass


def _git(repo: Path, *args: str, binario: bool = False):
    r = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=not binario,
        errors=None if binario else "replace",
    )
    if r.returncode != 0:
        err = r.stderr.decode(errors="replace") if binario else r.stderr
        raise ErrorDeGit(f"git {' '.join(args)} falló: {err.strip()}")
    return r.stdout


def dir_de_git(repo: Path) -> Path:
    ruta = Path(_git(repo, "rev-parse", "--absolute-git-dir").strip())
    return ruta


# ── Escaneo del índice ───────────────────────────────────────────────────────

def archivos_en_staging(repo: Path) -> list[str]:
    """Lo que este commit va a agregar o modificar.

    `--diff-filter=ACMR` excluye las bajas: un archivo que se está borrando no
    entra al historial de nuevo, así que bloquear el commit que lo saca sería
    exactamente al revés.
    """
    salida = _git(repo, "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")
    return [r for r in salida.split("\0") if r]


def _contenido_en_index(repo: Path, ruta: str) -> str | None:
    """El contenido tal como quedó en el índice, no el del árbol de trabajo.

    `git add` seguido de una edición dejaría al hook mirando algo distinto de lo
    que se está por commitear.
    """
    try:
        crudo = _git(repo, "show", f":{ruta}", binario=True)
    except ErrorDeGit:
        return None
    if len(crudo) > ss.MAX_BYTES:
        return None
    return crudo.decode("utf-8", errors="replace")


def escanear_staging(repo: Path, reglas: list[ss.Regla]) -> ss.Reporte:
    entradas = [
        ss.Entrada(ruta, _contenido_en_index(repo, ruta))
        for ruta in archivos_en_staging(repo)
    ]
    return ss.escanear(entradas, reglas)


# ── Marca y registro de salteos ──────────────────────────────────────────────

def _arbol_del_indice(repo: Path) -> str:
    """El tree del índice. `write-tree` crea el objeto sin mover HEAD ni el índice."""
    return _git(repo, "write-tree").strip()


def aprobar(repo: Path) -> None:
    (dir_de_git(repo) / MARCA).write_text(_arbol_del_indice(repo))


def salteos(repo: Path) -> list[str]:
    archivo = dir_de_git(repo) / REGISTRO
    return archivo.read_text(encoding="utf-8").splitlines() if archivo.exists() else []


def registrar_salteo(repo: Path) -> bool:
    """Post-commit: anota si el commit recién hecho no pasó por el escaneo.

    Devuelve True si registró un salteo. Consume la marca en cualquier caso, para
    que el próximo commit tenga que aprobarse por sí mismo.
    """
    gitdir = dir_de_git(repo)
    marca = gitdir / MARCA
    aprobado = marca.read_text().strip() if marca.exists() else ""
    marca.unlink(missing_ok=True)

    try:
        arbol = _git(repo, "rev-parse", "HEAD^{tree}").strip()
        commit = _git(repo, "rev-parse", "--short", "HEAD").strip()
    except ErrorDeGit:
        return False

    if aprobado == arbol:
        return False

    cuando = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with (gitdir / REGISTRO).open("a", encoding="utf-8") as f:
        f.write(f"{cuando}  {commit}  escaneo salteado ({SALTEO} o hook ausente)\n")
    return True


# ── Mensajes ─────────────────────────────────────────────────────────────────

def formatear(reporte: ss.Reporte, previos: list[str]) -> str:
    lineas: list[str] = []

    for categoria in ss.CATEGORIAS:
        hallazgos = [h for h in reporte.hallazgos if h.categoria == categoria]
        if not hallazgos:
            continue
        verbo = "bloquea el commit" if categoria in ss.BLOQUEANTES else "advertencia"
        lineas.append(f"{categoria} — {verbo}:")
        for h in hallazgos:
            donde = f"{h.ruta}:{h.linea}" if h.linea else h.ruta
            lineas.append(f"  {donde}")
            lineas.append(f"    regla:   {h.regla}")
            if h.evidencia:
                lineas.append(f"    línea:   {h.evidencia}")
            lineas.append(f"    remedio: {h.remedio}")
        lineas.append("")

    if reporte.bloqueantes:
        lineas += [
            f"Para saltearlo deliberadamente: {SALTEO}",
            "El salteo queda registrado; podés verlo con este mismo script (--salteos).",
        ]
        if previos:
            lineas += [
                "",
                f"Ya hay {len(previos)} salteo(s) registrado(s) antes de éste:",
                *(f"  {s}" for s in previos[-3:]),
            ]
    return "\n".join(lineas)


# ── Instalación ──────────────────────────────────────────────────────────────

def instalar(repo: Path) -> str:
    """Apunta core.hooksPath al directorio versionado. Idempotente.

    Es config local, así que un clon nuevo no la trae: la llama /awi-update, que
    ya es el camino por el que el harness llega a una instancia.
    """
    actual = subprocess.run(
        ["git", "-C", str(repo), "config", "--get", "core.hooksPath"],
        capture_output=True,
        text=True,
    ).stdout.strip()
    if actual == HOOKS_RELDIR:
        return f"ya instalado (core.hooksPath = {HOOKS_RELDIR})"
    _git(repo, "config", "core.hooksPath", HOOKS_RELDIR)
    return f"core.hooksPath = {HOOKS_RELDIR}" + (f" (antes: {actual})" if actual else "")


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    from paths import AWI_ROOT

    p = argparse.ArgumentParser(description="Escaneo del índice antes de commitear.")
    p.add_argument("--repo", default=".", type=Path)
    p.add_argument("--reglas", type=Path, default=AWI_ROOT / ss.REGLAS_SENSIBLES)
    p.add_argument("--hook", action="store_true", help="modo pre-commit")
    p.add_argument("--registrar-salteo", action="store_true", help="modo post-commit")
    p.add_argument("--salteos", action="store_true", help="listar los salteos registrados")
    p.add_argument("--instalar", action="store_true", help="apuntar core.hooksPath")
    args = p.parse_args(argv)

    try:
        if args.instalar:
            print(instalar(args.repo))
            return 0

        if args.salteos:
            registrados = salteos(args.repo)
            print("\n".join(registrados) if registrados else "Sin salteos registrados.")
            return 0

        if args.registrar_salteo:
            # Telemetría: nunca puede romper el commit que ya se hizo.
            try:
                if registrar_salteo(args.repo):
                    print("aviso: este commit no pasó por el escaneo de material sensible")
            except (ErrorDeGit, OSError):
                pass
            return 0

        reglas = ss.cargar_reglas(args.reglas)
        reporte = escanear_staging(args.repo, reglas)
    except (ss.ReglasInvalidas, ErrorDeGit) as e:
        # Un hook que falla por su propia culpa no puede trabar el trabajo, pero
        # tampoco puede aprobar en silencio: avisa y deja pasar sin marca, así
        # el post-commit lo registra como no escaneado.
        print(f"escaneo de material sensible: {e}", file=sys.stderr)
        return 0

    if reporte.hallazgos:
        print(formatear(reporte, salteos(args.repo)), file=sys.stderr)
    if reporte.bloqueantes:
        return 1

    aprobar(args.repo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
