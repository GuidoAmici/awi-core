#!/usr/bin/env python3
"""Registrar qué skill se invocó — desde código, no por instrucción.

`log_command` se invocaba **por instrucción**: 23 archivos `SKILL.md` le piden al
agente que lo llame, y el registro depende de que el agente obedezca. El resultado
es que subcuenta, y esa imprecisión importa justo cuando se la necesita: de 40
skills, 11 tienen evidencia de uso en 272 invocaciones registradas. Las otras 29
no aparecen ni una vez, y sin un registro confiable no se puede distinguir «no se
usa» de «se usó y no se anotó».

La razón para moverlo es la misma que la fase 1 aplicó al ciclo de contexto: **el
juicio va en instrucciones, la mecánica en código.** Registrar una invocación es
mecánica.

Corre como hook `UserPromptSubmit`, así que ve lo que el operador escribió antes de
que el agente decida nada. Lo que gana en confiabilidad lo paga en alcance: ve las
invocaciones del operador, no las que un agente hace por su cuenta. Es el
intercambio correcto — la pregunta que hay que contestar es «qué skills usa el
operador».

**Nunca falla ruidosamente.** Es telemetría, y la telemetría no puede romper la
función que instrumenta: cualquier error se traga y el prompt sigue.

Ver PRD 4 (issue #83), subissue #102.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1].parent
sys.path.insert(0, str(RAIZ / ".claude/skills/shared/scripts"))

#: `/today`, `/awi-org newhaze`, `/code-review ultra 42`. El nombre puede tener
#: guiones y dos puntos (las skills de plugin son `plugin:skill`).
INVOCACION = re.compile(r"^\s*/([a-zA-Z][a-zA-Z0-9:_-]*)")


def skill_invocada(prompt: str) -> str | None:
    m = INVOCACION.match(prompt or "")
    return m.group(1) if m else None


def main() -> int:
    try:
        entrada = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    # Un JSON válido que no es un objeto —`[]`, `"algo"`, `null`— llegó a romper
    # esto, y el test lo encontró. Un hook que revienta ante una entrada rara es
    # un tapón en el camino del prompt.
    if not isinstance(entrada, dict):
        return 0

    nombre = skill_invocada(entrada.get("prompt") or "")
    if not nombre:
        return 0

    try:
        from log_command import registrar

        registrar(nombre, "invoked", fuente="prompt")
    except Exception:
        # Telemetría: nunca puede romper el prompt que instrumenta.
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
