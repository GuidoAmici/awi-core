"""Activar y desactivar un repo del manifiesto — orgs y codebases.

Reemplaza a los tres `toggle_client.py` duplicados, que descubrían los repos
registrados con `git submodule status` y fallaban con «no registrado en
.gitmodules» — un archivo que el [ADR 0009](../../../../docs/adr/0009-manifiestos-json-en-lugar-de-submodulos.md)
eliminó. Su función era leer un registro inexistente: togglear un codebase no
funcionaba, y el error hablaba de un mecanismo que ya no existe.

Es el mismo movimiento que la fase 1 hizo con el ciclo de contexto: dejar de
parsear `.gitmodules` y usar los manifiestos. El descubrimiento ya existe y está
probado en `manifest.plan()`.

**Desactivar no borra.** Marca la entrada como inactiva en el manifiesto; el
directorio queda como está. El operador puede borrarlo si quiere, pero eso es su
decisión y no un efecto de haber togglado algo.

Uso:
    python3 toggle_repo.py status
    python3 toggle_repo.py enable <nombre>
    python3 toggle_repo.py disable <nombre>
    python3 toggle_repo.py enable <org>/<codebase>

Ver PRD 4 (issue #83), subissue #100.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import manifest
from paths import AWI_ROOT, USER_SUBMODULES_FILE, USERS_RELDIR


class RepoDesconocido(KeyError):
    """Nombre que el manifiesto no declara. El mensaje lista las opciones válidas."""


@dataclass(frozen=True)
class Entrada:
    """Un repo togglable. `org` es None para las entradas de primer nivel."""

    nombre: str
    activo: bool
    tipo: str
    org: str | None = None
    materializado: bool = False

    @property
    def clave(self) -> str:
        return f"{self.org}/{self.nombre}" if self.org else self.nombre


def _manifiesto(awi_root: Path) -> Path:
    """El user-submodules.json del operador logueado."""
    _, github_id, _ = manifest.load_submodules(awi_root)
    return awi_root / USERS_RELDIR / github_id / USER_SUBMODULES_FILE


def _leer(ruta: Path) -> dict:
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise RepoDesconocido(f"no existe el manifiesto {ruta}: ¿corriste /awi-user?") from e


def _escribir(ruta: Path, datos: dict) -> None:
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def listar(awi_root: Path) -> list[Entrada]:
    """Todo lo togglable, descubierto del manifiesto y no de `.gitmodules`."""
    ruta = _manifiesto(awi_root)
    datos = _leer(ruta)
    entradas: list[Entrada] = []

    for nombre, cfg in datos.get("submodules", {}).items():
        destino = awi_root / cfg.get("path", "")
        entradas.append(
            Entrada(
                nombre=nombre,
                activo=bool(cfg.get("active", False)),
                tipo=manifest.entry_type(cfg),
                materializado=manifest.is_mounted(destino),
            )
        )
        for cb_nombre, cb in (cfg.get("codebases") or {}).items():
            entradas.append(
                Entrada(
                    nombre=cb_nombre,
                    activo=bool(cb.get("active", False)),
                    tipo="codebase",
                    org=nombre,
                    materializado=manifest.is_mounted(
                        destino / manifest.CODEBASE_SUBDIR / cb_nombre
                    ),
                )
            )
    return entradas


def _resolver(entradas: list[Entrada], nombre: str) -> Entrada:
    """Por clave exacta `org/codebase`, o por nombre si no es ambiguo."""
    exacta = [e for e in entradas if e.clave == nombre]
    if exacta:
        return exacta[0]

    por_nombre = [e for e in entradas if e.nombre == nombre]
    if len(por_nombre) == 1:
        return por_nombre[0]
    if len(por_nombre) > 1:
        raise RepoDesconocido(
            f"«{nombre}» es ambiguo: existe en {', '.join(e.clave for e in por_nombre)}. "
            "Usá la forma org/codebase."
        )
    raise RepoDesconocido(
        f"el manifiesto no declara «{nombre}». Los declarados son: "
        f"{', '.join(sorted(e.clave for e in entradas)) or '(ninguno)'}."
    )


def togglear(awi_root: Path, nombre: str, activo: bool) -> Entrada:
    """Cambia el estado en el manifiesto y devuelve la entrada resultante."""
    ruta = _manifiesto(awi_root)
    datos = _leer(ruta)
    entrada = _resolver(listar(awi_root), nombre)

    if entrada.org:
        cfg = datos["submodules"][entrada.org].setdefault("codebases", {})
        cfg.setdefault(entrada.nombre, {})["active"] = activo
    else:
        datos["submodules"][entrada.nombre]["active"] = activo

    _escribir(ruta, datos)
    return Entrada(
        nombre=entrada.nombre, activo=activo, tipo=entrada.tipo,
        org=entrada.org, materializado=entrada.materializado,
    )


def formatear(entradas: list[Entrada]) -> str:
    if not entradas:
        return "El manifiesto no declara ningún repo."
    lineas = []
    for e in sorted(entradas, key=lambda e: (e.org or "", e.nombre)):
        estado = "activo  " if e.activo else "inactivo"
        disco = "en disco" if e.materializado else "sin materializar"
        lineas.append(f"  {estado}  {e.clave:34} {e.tipo:14} {disco}")
    return "Repos del manifiesto:\n" + "\n".join(lineas)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Activar o desactivar un repo del manifiesto.")
    p.add_argument("accion", choices=["enable", "disable", "status"])
    p.add_argument("nombre", nargs="?", help="nombre, u org/codebase si es ambiguo")
    p.add_argument("--raiz", type=Path, default=AWI_ROOT)
    args = p.parse_args(argv)

    try:
        if args.accion == "status":
            print(formatear(listar(args.raiz)))
            return 0

        if not args.nombre:
            print(f"error: «{args.accion}» necesita un nombre", file=sys.stderr)
            return 2

        entrada = togglear(args.raiz, args.nombre, args.accion == "enable")
    except RepoDesconocido as e:
        print(f"error: {e.args[0]}", file=sys.stderr)
        return 1

    if entrada.activo:
        print(f"«{entrada.clave}» quedó activo. Corré /awi-initialize para materializarlo.")
    else:
        print(
            f"«{entrada.clave}» quedó inactivo. El directorio no se tocó: "
            "desactivar no borra nada."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
