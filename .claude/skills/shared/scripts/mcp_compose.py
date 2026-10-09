#!/usr/bin/env python3
"""Arma el .mcp.json de la raíz con los MCP de AWI y los de cada org activa.

Claude Code sólo lee el .mcp.json de la raíz del proyecto: uno dentro de
_data/organizations/<org>/ no lo carga ninguna sesión que trabaje desde AWI.
Por eso cada org declara sus MCP en su propio repo (`mcp.json`, misma forma
que .mcp.json) y este script los junta con los de AWI (`.mcp.base.json`).

.mcp.json queda generado y fuera de git: se edita .mcp.base.json o el
mcp.json de la org, nunca el resultado. Una org inactiva no aporta sus MCP.
Un nombre repetido es un error: una org no pisa un MCP de AWI ni de otra org.

El cambio lo toma Claude Code al arrancar la sesión siguiente (o desde /mcp).

Uso:  python3 .claude/skills/shared/scripts/mcp_compose.py [--check]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from paths import AWI_ROOT
from manifest import active_entries, entry_type, load_submodules

BASE_FILE = ".mcp.base.json"
OUTPUT_FILE = ".mcp.json"
ORG_FILE = "mcp.json"


class NombreRepetido(Exception):
    pass


def _servidores(path: Path) -> dict:
    """Los mcpServers de un archivo con la forma de .mcp.json. Sin archivo → {}."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8")).get("mcpServers", {})


def componer(raiz: Path) -> tuple[dict, list[str]]:
    """Devuelve (contenido de .mcp.json, fuentes usadas en orden)."""
    servidores = dict(_servidores(raiz / BASE_FILE))
    origen = {nombre: BASE_FILE for nombre in servidores}
    fuentes = [BASE_FILE]

    entries, _, _ = load_submodules(raiz)
    for org, entry in sorted(active_entries(entries).items()):
        if entry_type(entry) != "org-workspace":
            continue
        archivo = raiz / entry.get("path", "") / ORG_FILE
        propios = _servidores(archivo)
        if not propios:
            continue
        rel = archivo.relative_to(raiz).as_posix()
        for nombre, config in propios.items():
            if nombre in servidores:
                raise NombreRepetido(
                    f"el MCP «{nombre}» de {rel} ya lo declara {origen[nombre]}"
                )
            servidores[nombre] = config
            origen[nombre] = rel
        fuentes.append(rel)

    return {"mcpServers": servidores}, fuentes


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--check", action="store_true",
                   help="no escribe: sale con 1 si .mcp.json está desactualizado")
    p.add_argument("--raiz", type=Path, default=AWI_ROOT)
    args = p.parse_args(argv)

    try:
        contenido, fuentes = componer(args.raiz)
    except NombreRepetido as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    texto = json.dumps(contenido, ensure_ascii=False, indent=2) + "\n"
    destino = args.raiz / OUTPUT_FILE
    actual = destino.read_text(encoding="utf-8") if destino.exists() else ""

    if args.check:
        if actual != texto:
            print(f"{OUTPUT_FILE} está desactualizado: corré mcp_compose.py", file=sys.stderr)
            return 1
        return 0

    if actual != texto:
        destino.write_text(texto, encoding="utf-8")
        print(f"{OUTPUT_FILE} regenerado con {len(contenido['mcpServers'])} MCP "
              f"de: {', '.join(fuentes)}. Recargá con /mcp o reiniciá la sesión.")
    else:
        print(f"{OUTPUT_FILE} ya estaba al día.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
