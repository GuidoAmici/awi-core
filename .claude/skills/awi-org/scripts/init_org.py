#!/usr/bin/env python3
"""Envoltorio fino: elige los parámetros, el módulo compartido hace la mecánica.

La lógica vivía cuatro veces —`awi-client`, `awi-org`, `new-client` e
`initialize`— con tres scripts byte-idénticos. Ahora vive en
`.claude/skills/shared/scripts/scaffold.py`, y esto sólo decide dónde y con qué
nombre. Ver PRD 4 (issue #83).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared" / "scripts"))
import scaffold
from paths import ORGANIZATIONS_RELDIR


def main() -> int:
    p = argparse.ArgumentParser(description="Scaffolding de un Org Workspace de AWI")
    p.add_argument("name", help="Slug de la organización (newhaze, afin, acme-corp)")
    p.add_argument("path", nargs="?", default=ORGANIZATIONS_RELDIR,
                   help=f"Directorio padre (por defecto {ORGANIZATIONS_RELDIR}/)")
    p.add_argument("--url", help="Remoto de GitHub, para registrarlo en el manifiesto")
    p.add_argument("--manifiesto", type=Path, help="user-submodules.json del operador")
    p.add_argument("--branch", default="main")
    args = p.parse_args()

    try:
        resultado = scaffold.scaffold(
            args.name, Path(args.path), args.url, args.manifiesto, args.branch
        )
    except scaffold.ScaffoldFallido as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(scaffold.describir(resultado, args.name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
