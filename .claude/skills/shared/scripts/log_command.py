#!/usr/bin/env python3
"""Registro de invocaciones de skills.

Dos formas de escribir acá, y el corte importa:

**Desde código** — el hook `UserPromptSubmit` (`.claude/hooks/log-skill-use.py`)
registra cada `/<skill>` que el operador escribe. Es mecánica, así que no depende
de que nadie se acuerde. Esta es la fuente confiable.

**Desde una skill** — una skill puede agregar cómo terminó (`completed`,
`skipped`, `errored`), que el hook no puede saber. Es información que mejora el
registro si está, y que si falta no lo invalida.

El movimiento de instrucción a código es del PRD 4 (issue #83, subissue #102). El
registro subcontaba porque 23 archivos `SKILL.md` le pedían al agente que lo
llamara, y de 40 skills sólo 11 aparecían en 272 invocaciones. Esa imprecisión es
un problema en sí misma: la única telemetría de qué se usa era poco confiable
justo cuando se la necesita para decidir qué borrar.

**Nunca levanta.** Es telemetría: un registro corrupto o un disco lleno no pueden
tumbar la skill que lo llama. `registrar()` devuelve si pudo escribir.

Uso (compatible con lo que las skills ya invocan):
    python3 log_command.py <command> <outcome>
    python3 log_command.py --conteo
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import CURRENT_USER, USERS_DIR

CURRENT_USER_FILE = CURRENT_USER
VALID_OUTCOMES = {"completed", "skipped", "errored", "invoked"}

ARCHIVO = "command-log.jsonl"


def resolve_github_id() -> str:
    """Read github-id from current-user.json."""
    if not CURRENT_USER_FILE.exists():
        raise FileNotFoundError(
            f"current-user.json not found at {CURRENT_USER_FILE}. Run /awi-user first."
        )
    data = json.loads(CURRENT_USER_FILE.read_text())
    github_id = data.get("github-id")
    if not github_id:
        raise ValueError("github-id not found in current-user.json")
    return str(github_id)


def registrar(command: str, outcome: str, fuente: str = "skill") -> bool:
    """Anota una línea. Devuelve si pudo, y nunca levanta.

    `fuente` distingue lo que escribió el hook de lo que escribió una skill, que
    es lo que permite medir cuánto subcontaba el registro anterior.
    """
    try:
        log_dir = USERS_DIR / resolve_github_id()
        log_dir.mkdir(parents=True, exist_ok=True)
        entrada = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M"),
            "command": command,
            "outcome": outcome,
            "fuente": fuente,
        }
        with (log_dir / ARCHIVO).open("a", encoding="utf-8") as f:
            f.write(json.dumps(entrada, ensure_ascii=False) + "\n")
        return True
    except Exception:
        return False


def leer(archivo: Path) -> list[dict]:
    """Las entradas parseables del registro, salteando las que no lo son.

    Un registro con una línea corrupta —un write interrumpido— no puede volverse
    ilegible por completo: la telemetría existente es demasiado escasa para
    descartarla entera por una línea.
    """
    if not archivo.exists():
        return []
    entradas = []
    for linea in archivo.read_text(encoding="utf-8", errors="replace").splitlines():
        linea = linea.strip()
        if not linea:
            continue
        try:
            dato = json.loads(linea)
        except json.JSONDecodeError:
            continue
        if isinstance(dato, dict) and dato.get("command"):
            entradas.append(dato)
    return entradas


def conteo(archivo: Path) -> dict[str, int]:
    """Cuántas veces se invocó cada skill, de más a menos."""
    total: dict[str, int] = {}
    for e in leer(archivo):
        total[e["command"]] = total.get(e["command"], 0) + 1
    return dict(sorted(total.items(), key=lambda kv: (-kv[1], kv[0])))


#: Nombre histórico, conservado porque las skills lo invocan por CLI y algún
#: script podría importarlo.
log_command = registrar


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--conteo":
        try:
            archivo = USERS_DIR / resolve_github_id() / ARCHIVO
        except Exception as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        datos = conteo(archivo)
        if not datos:
            print("Sin invocaciones registradas.")
            return 0
        for nombre, veces in datos.items():
            print(f"{veces:5}  {nombre}")
        return 0

    if len(sys.argv) != 3:
        print("Usage: log_command.py <command> <outcome> | --conteo", file=sys.stderr)
        print(f"Valid outcomes: {', '.join(sorted(VALID_OUTCOMES))}", file=sys.stderr)
        return 1

    command, outcome = sys.argv[1], sys.argv[2]
    if outcome not in VALID_OUTCOMES:
        print(
            f"Invalid outcome '{outcome}'. Valid: {', '.join(sorted(VALID_OUTCOMES))}",
            file=sys.stderr,
        )
        return 1

    registrar(command, outcome)
    return 0


if __name__ == "__main__":
    sys.exit(main())
