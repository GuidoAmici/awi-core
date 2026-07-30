"""Verificación contra la deriva de la capa de contexto.

El mismo motor que las reglas de material sensible, con otro conjunto de reglas.
Lo que busca es vocabulario que describe mecanismos eliminados: un agente que lee
`CONTEXT.md` para decidir cómo materializar un repo no puede recibir
instrucciones de un mecanismo que se fue hace dos ADRs.

Existe porque las dos instancias de deriva que la revisión integral encontró
mientras trabajaba —`INSTRUCTIONS.md` explicando el protocolo de `.gitmodules`, y
`delegation.md` apuntando a un script inexistente— se encontraron **por
casualidad**, al pasar por ahí para otra cosa. Este verificador existe para que la
próxima no dependa de la casualidad.

Uso:
    python3 .claude/skills/shared/scripts/vocab_check.py [--raiz .] [--json]

Sale con 1 si hay vocabulario eliminado. El vocabulario dudoso sólo advierte.

Ver PRD 3 (issue #82), subissues #95 a #98.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import sensitive_scan as ss

#: Dónde vive la capa de contexto: los documentos que un agente lee para decidir.
#: No es «todo el repo» a propósito — el objetivo es lo que se consulta, no lo que
#: se archiva.
AMBITOS = (
    "CONTEXT.md",
    "CONTEXT-MAP.md",
    "README.md",
    "CLAUDE.md",
    ".claude/skills/**/*.md",
    ".claude/hooks/**/*.md",
    "_system/**/*.md",
    "docs/**/*.md",
)

#: Árboles que nunca se verifican: clones de terceros y datos privados.
FUERA = ("_data/", "_system/agency-agents/", "node_modules/", ".git/")


def documentos(raiz: Path) -> list[Path]:
    """Los documentos de contexto, sin duplicados y en orden estable."""
    vistos: dict[Path, None] = {}
    for patron in AMBITOS:
        for p in sorted(raiz.glob(patron)):
            if not p.is_file():
                continue
            rel = p.relative_to(raiz).as_posix()
            if any(rel.startswith(x) or f"/{x}" in f"/{rel}" for x in FUERA):
                continue
            vistos.setdefault(p, None)
    return list(vistos)


def verificar(raiz: Path, reglas: list[ss.Regla]) -> ss.Reporte:
    entradas = []
    for doc in documentos(raiz):
        try:
            texto = doc.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        entradas.append(ss.Entrada(doc.relative_to(raiz).as_posix(), texto))
    return ss.escanear(entradas, reglas)


def formatear(reporte: ss.Reporte, raiz: Path, revisados: int) -> str:
    if not reporte.hallazgos:
        return f"Vocabulario al día — {revisados} documento(s) revisados en {raiz}."

    lineas = [f"Deriva de vocabulario en {raiz} ({revisados} documento(s) revisados)", ""]
    for categoria in reporte.categorias:
        hallazgos = [h for h in reporte.hallazgos if h.categoria == categoria]
        if not hallazgos:
            continue
        marca = "BLOQUEA" if hallazgos[0].bloquea else "advierte"
        lineas.append(f"── {categoria} ({len(hallazgos)}) · {marca}")
        for h in sorted(hallazgos, key=lambda h: (h.ruta, h.linea or 0)):
            lineas.append(f"   {h.ruta}:{h.linea}")
            lineas.append(f"      {h.evidencia}")
            lineas.append(f"      → {h.remedio}")
        lineas.append("")
    return "\n".join(lineas)


def main(argv: list[str] | None = None) -> int:
    from paths import AWI_ROOT

    p = argparse.ArgumentParser(description="Detecta vocabulario de mecanismos eliminados.")
    p.add_argument("--raiz", default=AWI_ROOT, type=Path)
    p.add_argument("--reglas", type=Path, default=None)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    reglas_path = args.reglas or (args.raiz / ss.REGLAS_VOCABULARIO)
    try:
        reglas = ss.cargar_reglas(reglas_path)
    except ss.ReglasInvalidas as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    reporte = verificar(args.raiz, reglas)
    revisados = len(documentos(args.raiz))

    if args.json:
        print(
            json.dumps(
                {
                    "revisados": revisados,
                    "conteo": reporte.por_categoria(),
                    "hallazgos": [
                        {
                            "ruta": h.ruta,
                            "linea": h.linea,
                            "regla": h.regla,
                            "categoria": h.categoria,
                            "evidencia": h.evidencia,
                            "remedio": h.remedio,
                            "bloquea": h.bloquea,
                        }
                        for h in reporte.hallazgos
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(formatear(reporte, args.raiz, revisados))

    return 1 if reporte.bloqueantes else 0


if __name__ == "__main__":
    sys.exit(main())
