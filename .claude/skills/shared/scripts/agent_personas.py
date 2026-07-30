"""Descubrimiento de personas-agente desde el árbol, sin registro intermedio.

Reemplaza a `.claude/reference/employees.json`, que listaba 36 entradas a mano
con su `path` y su `tagline`. El [ADR 0008](../../../docs/adr/0008-agent-discovery-desde-agency-agents.md)
decidió descubrir desde `_system/agency-agents/` y el registro quedó igual, vivo
y leído por dos skills — el patrón de residuo que el ADR 0013 diagnosticó: la
decisión se tomó y la migración no se completó.

Un registro escrito a mano sobre un árbol de 292 archivos que un tercero puede
cambiar sin aviso está desactualizado por construcción. Acá el árbol **es** el
registro: el archivo del agente es su prompt de sistema, su directorio es su
categoría, y su `description` del frontmatter es el tagline que sirve para
rutear. Agregar una persona-agente es agregar un archivo.

Uso:
    python3 .claude/skills/shared/scripts/agent_personas.py            # todas
    python3 .claude/skills/shared/scripts/agent_personas.py backend    # buscar
    python3 .claude/skills/shared/scripts/agent_personas.py --categorias

Ver PRD 3 (issue #82), subissue #97.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

#: Dónde vive el árbol de personas-agente, relativo a la raíz de AWI.
AGENCY_RELDIR = "_system/agency-agents"

#: Directorios del repo de terceros que no contienen personas-agente.
NO_ES_CATEGORIA = {".git", ".github", "scripts", "examples", "docs", "assets"}

#: Archivos de nivel de repo que no son personas-agente.
NO_ES_PERSONA = {"README", "CONTRIBUTING", "SECURITY", "LICENSE", "CHANGELOG", "CODE_OF_CONDUCT"}


class ArbolAusente(RuntimeError):
    """`_system/agency-agents/` no está materializado. Falla ruidosamente."""


@dataclass(frozen=True)
class Persona:
    """Una persona-agente. `nombre` es la clave con la que se la referencia."""

    nombre: str
    categoria: str
    ruta: Path
    tagline: str

    def __str__(self) -> str:
        return f"{self.nombre} ({self.categoria}) — {self.tagline}"


def _frontmatter(texto: str) -> dict[str, str]:
    """Los pares clave: valor del frontmatter YAML, sin dependencias.

    Basta para lo que hace falta: `description` es una línea. Un parser de YAML
    completo sería más de lo necesario para leer un tagline.
    """
    lineas = texto.splitlines()
    if not lineas or lineas[0].strip() != "---":
        return {}
    campos: dict[str, str] = {}
    for linea in lineas[1:]:
        if linea.strip() == "---":
            break
        clave, sep, valor = linea.partition(":")
        if sep and not clave.startswith(" "):
            campos[clave.strip()] = valor.strip()
    return campos


def _nombre(ruta: Path, categoria: str) -> str:
    """La clave de referencia: el nombre del archivo sin su prefijo de categoría.

    Los archivos vienen prefijados por su categoría (`engineering-ai-engineer.md`),
    que es redundante con el directorio. `ai-engineer` es la clave que el registro
    eliminado usaba, así que las referencias existentes en los issues siguen
    resolviendo.
    """
    tallo = ruta.stem
    prefijo = f"{categoria}-"
    return tallo[len(prefijo):] if tallo.startswith(prefijo) else tallo


def descubrir(awi_root: Path) -> list[Persona]:
    """Todas las personas-agente del árbol, ordenadas por categoría y nombre."""
    raiz = awi_root / AGENCY_RELDIR
    if not raiz.is_dir():
        raise ArbolAusente(
            f"no está materializado {raiz}. Es un repo upstream declarado en el "
            "manifiesto: corré /awi-initialize."
        )

    personas: list[Persona] = []
    for categoria_dir in sorted(p for p in raiz.iterdir() if p.is_dir()):
        if categoria_dir.name in NO_ES_CATEGORIA or categoria_dir.name.startswith("."):
            continue
        categoria = categoria_dir.name
        for md in sorted(categoria_dir.rglob("*.md")):
            if md.stem in NO_ES_PERSONA or md.stem.upper() in NO_ES_PERSONA:
                continue
            try:
                campos = _frontmatter(md.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                continue
            if not campos.get("name") and not campos.get("description"):
                continue  # documento del repo, no una persona-agente
            personas.append(
                Persona(
                    nombre=_nombre(md, categoria),
                    categoria=categoria,
                    ruta=md.relative_to(awi_root),
                    tagline=campos.get("description", "").rstrip("."),
                )
            )
    return personas


def resolver(awi_root: Path, nombre: str) -> Persona:
    """Una persona-agente por su nombre.

    Falla nombrando alternativas: un error que dice «no existe» y nada más
    obliga a ir a leer el árbol a mano.
    """
    personas = descubrir(awi_root)
    exacta = [p for p in personas if p.nombre == nombre]
    if exacta:
        return exacta[0]

    parecidas = [p.nombre for p in personas if nombre.lower() in p.nombre.lower()][:8]
    sugerencia = f" ¿Quisiste decir {', '.join(parecidas)}?" if parecidas else ""
    raise KeyError(
        f"no hay ninguna persona-agente «{nombre}» en {AGENCY_RELDIR}/.{sugerencia}"
    )


def buscar(awi_root: Path, termino: str) -> list[Persona]:
    """Personas cuyo nombre, categoría o tagline mencionan el término."""
    t = termino.lower()
    return [
        p
        for p in descubrir(awi_root)
        if t in p.nombre.lower() or t in p.categoria.lower() or t in p.tagline.lower()
    ]


def main(argv: list[str] | None = None) -> int:
    from paths import AWI_ROOT

    p = argparse.ArgumentParser(description="Personas-agente disponibles.")
    p.add_argument("termino", nargs="?", help="filtrar por nombre, categoría o tagline")
    p.add_argument("--raiz", type=Path, default=AWI_ROOT)
    p.add_argument("--categorias", action="store_true", help="sólo listar las categorías")
    p.add_argument("--resolver", metavar="NOMBRE", help="devolver la ruta de una persona")
    args = p.parse_args(argv)

    try:
        if args.resolver:
            print(resolver(args.raiz, args.resolver).ruta)
            return 0

        personas = buscar(args.raiz, args.termino) if args.termino else descubrir(args.raiz)
    except (ArbolAusente, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if args.categorias:
        for categoria in sorted({p.categoria for p in personas}):
            cuantas = sum(1 for x in personas if x.categoria == categoria)
            print(f"{categoria:24} {cuantas}")
        return 0

    if not personas:
        print("Sin coincidencias.")
        return 1
    for persona in personas:
        print(f"{persona.nombre:38} {persona.categoria:22} {persona.tagline[:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
