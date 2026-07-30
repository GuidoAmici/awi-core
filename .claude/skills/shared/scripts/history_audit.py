"""Inventario de material sensible en el historial completo de un repo.

Es la única pieza del PRD 1 que sabe de git. Toda la definición de «sensible»
vive en `sensitive_scan`, que no sabe de git: acá sólo se enumeran objetos y se
le pasan al motor.

Lo que hace distinta a esta auditoría de mirar el árbol de trabajo: recorre
`git rev-list --objects --all`, así que encuentra lo que **ya no está en HEAD**.
Que es exactamente la situación de awi-core — los objetos de `.claude/tmp/`
salieron del árbol en 8334bed y siguen en el historial de un repo público.

Uso:
    python3 .claude/skills/shared/scripts/history_audit.py [--repo RUTA] [--json]

Sale con 1 si hay hallazgos bloqueantes (credencial, material-de-cliente).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import sensitive_scan as ss

#: Advertencia que acompaña a todo reporte. No es decorativa: sin esto, un
#: reporte vacío después de purgar se lee como «el material dejó de existir»,
#: y no es lo que pasó.
LIMITE = """\
Límite de la purga — reescribir el historial NO garantiza borrado en GitHub.
Los objetos quedan sin referencia, pero siguen siendo accesibles por la API
durante un tiempo indeterminado, y sólo desaparecen del todo pidiéndoselo a
soporte o recreando el repositorio. La purga reduce la exposición futura; no la
revierte retroactivamente. Toda credencial que estuvo expuesta se considera
comprometida y se rota, independientemente de la purga."""


class ErrorDeGit(RuntimeError):
    pass


@dataclass(frozen=True)
class EntradaDeHistorial:
    """Una entrada para el motor, con el oid del blob como origen."""

    ruta: str
    contenido: str | None
    origen: str


def _git(repo: Path, *args: str, entrada: str | None = None) -> str:
    r = subprocess.run(
        ["git", "-C", str(repo), *args],
        input=entrada,
        capture_output=True,
        text=True,
        errors="replace",
    )
    if r.returncode != 0:
        raise ErrorDeGit(f"git {' '.join(args)} falló en {repo}: {r.stderr.strip()}")
    return r.stdout


def rutas_por_objeto(repo: Path, refs: tuple[str, ...] = ("--all",)) -> dict[str, set[str]]:
    """oid → todas las rutas con las que ese objeto apareció alguna vez.

    Dos fuentes, porque ninguna alcanza sola.

    `rev-list --objects` **deduplica objetos**: un blob que vivió en dos rutas se
    imprime una sola vez, con una de ellas. Eso hace que una regla de ruta pierda
    la otra, y no es teórico — pasó. El blob vacío aparecía con una única ruta, y
    `.claude/tmp/delegates/skill-quality-audit/output.log` sobrevivió a la primera
    purga por eso: la ruta nunca entró al inventario.

    `log --raw` da el par (blob, ruta) de cada cambio, que es como un archivo
    entra al historial, así que cubre todas las rutas. Se usan las dos y se unen:
    la primera aporta los objetos alcanzables que ningún cambio nombra, la
    segunda las rutas que la primera colapsó.
    """
    mapa: dict[str, set[str]] = {}

    for linea in _git(repo, "rev-list", "--objects", *refs).splitlines():
        oid, _, ruta = linea.partition(" ")
        if ruta:  # los commits y el tree raíz no tienen ruta
            mapa.setdefault(oid, set()).add(ruta)

    # --raw imprime `:<modo_viejo> <modo_nuevo> <oid_viejo> <oid_nuevo> <estado>\tRUTA`.
    # Interesan los dos oids: el nuevo es lo que el cambio agregó, el viejo es lo
    # que había antes en esa misma ruta.
    vacio = "0" * 40
    crudo = _git(repo, "log", "--raw", "--no-renames", "--no-abbrev", "--format=", *refs)
    for linea in crudo.splitlines():
        if not linea.startswith(":") or "\t" not in linea:
            continue
        meta, _, ruta = linea.partition("\t")
        campos = meta.split()
        if len(campos) < 5:
            continue
        for oid in (campos[2], campos[3]):
            if oid != vacio and not oid.startswith(vacio[:20]):
                mapa.setdefault(oid, set()).add(ruta)
    return mapa


def _blobs(repo: Path, oids: list[str]) -> dict[str, int]:
    """De los oids dados, los que son blob, con su tamaño."""
    if not oids:
        return {}
    salida = _git(repo, "cat-file", "--batch-check", entrada="\n".join(oids) + "\n")
    tamanos: dict[str, int] = {}
    for linea in salida.splitlines():
        partes = linea.split()
        if len(partes) == 3 and partes[1] == "blob":
            tamanos[partes[0]] = int(partes[2])
    return tamanos


def _contenidos(repo: Path, oids: list[str]) -> dict[str, str]:
    """Contenido de los blobs pedidos, en una sola invocación de git.

    `--batch` responde con `oid blob tamaño\\n<bytes>\\n` por objeto, así que el
    stream se consume por longitud declarada y no por delimitador.
    """
    if not oids:
        return {}
    r = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "--batch"],
        input=("\n".join(oids) + "\n").encode(),
        capture_output=True,
    )
    if r.returncode != 0:
        raise ErrorDeGit(f"git cat-file --batch falló: {r.stderr.decode(errors='replace')}")

    salida = r.stdout
    contenidos: dict[str, str] = {}
    i = 0
    while i < len(salida):
        fin = salida.find(b"\n", i)
        if fin == -1:
            break
        cabecera = salida[i:fin].split()
        i = fin + 1
        if len(cabecera) != 3:
            continue  # "missing": no consume cuerpo
        oid, tamano = cabecera[0].decode(), int(cabecera[2])
        contenidos[oid] = salida[i : i + tamano].decode("utf-8", errors="replace")
        i += tamano + 1  # el salto que git agrega después del cuerpo
    return contenidos


def auditar(
    repo: Path,
    reglas: list[ss.Regla],
    refs: tuple[str, ...] = ("--all",),
) -> ss.Reporte:
    """Recorre el historial y devuelve el reporte del motor."""
    mapa = rutas_por_objeto(repo, refs)
    tamanos = _blobs(repo, list(mapa))

    # Sólo se lee el contenido de lo que el motor puede aprovechar. El historial
    # se recorre en CI en cada push: leer 11 MB para nada sería un impuesto.
    legibles = [oid for oid, t in tamanos.items() if 0 < t <= ss.MAX_BYTES]
    contenidos = _contenidos(repo, legibles)

    entradas = [
        EntradaDeHistorial(ruta=ruta, contenido=contenidos.get(oid), origen=oid[:12])
        for oid in tamanos
        for ruta in sorted(mapa[oid])
    ]
    return ss.escanear(entradas, reglas)


# ── Reporte ──────────────────────────────────────────────────────────────────

def formatear(reporte: ss.Reporte, repo: Path) -> str:
    conteo = reporte.por_categoria()
    lineas = [f"Auditoría del historial de {repo}", ""]

    if not reporte.hallazgos:
        lineas += ["Sin hallazgos.", "", LIMITE]
        return "\n".join(lineas)

    for categoria in ss.CATEGORIAS:
        hallazgos = [h for h in reporte.hallazgos if h.categoria == categoria]
        if not hallazgos:
            continue
        marca = "BLOQUEA" if categoria in ss.BLOQUEANTES else "advierte"
        lineas.append(f"── {categoria} ({len(hallazgos)}) · {marca}")
        for h in sorted(hallazgos, key=lambda h: (h.regla, h.ruta)):
            donde = f"{h.ruta}:{h.linea}" if h.linea else h.ruta
            lineas.append(f"   {h.regla:24} {donde}  [{h.origen}]")
            if h.evidencia:
                lineas.append(f"   {'':24} └ {h.evidencia}")
        lineas.append("")

    lineas.append("Rutas distintas a purgar:")
    lineas += [f"   {r}" for r in reporte.rutas()]
    lineas += [
        "",
        "Conteo: " + ", ".join(f"{c}={conteo[c]}" for c in ss.CATEGORIAS),
        "",
        LIMITE,
    ]
    return "\n".join(lineas)


def como_json(reporte: ss.Reporte) -> str:
    return json.dumps(
        {
            "conteo": reporte.por_categoria(),
            "rutas": reporte.rutas(),
            "limite": LIMITE,
            "hallazgos": [
                {
                    "ruta": h.ruta,
                    "regla": h.regla,
                    "categoria": h.categoria,
                    "linea": h.linea,
                    "evidencia": h.evidencia,
                    "objeto": h.origen,
                    "bloquea": h.bloquea,
                    "remedio": h.remedio,
                }
                for h in reporte.hallazgos
            ],
        },
        ensure_ascii=False,
        indent=2,
    )


def main(argv: list[str] | None = None) -> int:
    from paths import AWI_ROOT

    p = argparse.ArgumentParser(description="Inventario de material sensible en el historial.")
    p.add_argument("--repo", default=".", type=Path, help="repo a auditar (por defecto, el actual)")
    p.add_argument(
        "--reglas",
        type=Path,
        default=AWI_ROOT / ss.REGLAS_SENSIBLES,
        help="archivo de reglas",
    )
    p.add_argument("--rev", action="append", default=None, help="refs a recorrer (por defecto --all)")
    p.add_argument("--json", action="store_true", help="salida para máquina")
    args = p.parse_args(argv)

    try:
        reglas = ss.cargar_reglas(args.reglas)
        reporte = auditar(args.repo, reglas, tuple(args.rev) if args.rev else ("--all",))
    except (ss.ReglasInvalidas, ErrorDeGit) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    print(como_json(reporte) if args.json else formatear(reporte, args.repo))
    return 1 if reporte.bloqueantes else 0


if __name__ == "__main__":
    sys.exit(main())
