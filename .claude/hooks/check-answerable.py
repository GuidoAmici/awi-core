#!/usr/bin/env python3
"""¿Este operador tiene `answerable`? Si no, que el agente se lo ofrezca.

`CLAUDE.md` dice que la forma de la respuesta la trae el plugin, y nada comprobaba
que estuviera. `/awi-introduction` no alcanza: se corta si `_data/` ya existe, así
que nunca llega a quien ya usa AWI. Un hook de `SessionStart` es lo único que le
llega a todos, en la primera sesión y en cualquier máquina nueva.

**Ofrece, no instala.** El alcance correcto es `user`, porque el valor del plugin es
regir también afuera de AWI (ADR 0022), y eso cambia las sesiones de todos los repos
de la máquina. Esa decisión es del operador. Por lo mismo, una instalación sólo de
proyecto cuenta como incompleta: `.claude/settings.json` la dispara al confiar en la
carpeta, y deja al operador sin el plugin en cualquier otro repo.

**Detecta leyendo `installed_plugins.json`, no con `claude plugin list`,** que tarda
3 segundos y se pagaría en cada sesión. El costo es depender de un formato interno:
si no se reconoce, el hook calla. Perder una oferta es mejor que insistir por error.

**El «no» queda en la config de usuario, junto a lo que decide:** la instalación es
por máquina y un worktree de AWI no comparte `.claude/tmp/` con el checkout principal.

No distingue sesiones delegadas: un `claude -p` hereda el entorno de quien lo lanzó,
incluido `CLAUDE_CODE_ENTRYPOINT`. Lo resuelve el texto de la oferta.

Uso:
    check-answerable.py            # hook: imprime la oferta si corresponde
    check-answerable.py instalar   # instala con alcance user
    check-answerable.py declinar   # no vuelve a ofrecer en esta máquina

El modo hook nunca falla ruidosamente: romper el arranque de la sesión es peor que
no ofrecer un plugin.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / ".claude/skills/shared/scripts"))

from paths import claude_config_dir  # noqa: E402

PLUGIN = "answerable@awi"
MARKETPLACE = "awi"
REPO = "GuidoAmici/awi-core"
ESTE_SCRIPT = ".claude/hooks/check-answerable.py"
REGLAS = "plugins/answerable/rules/answerable.md"


def _leer_json(ruta: Path):
    """El contenido del archivo, o None si no se pudo leer."""
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def marca_declinado() -> Path:
    return claude_config_dir() / "awi" / "answerable-declined"


def instalacion() -> dict:
    """Qué dice Claude Code del plugin: `instalado`, `proyectos` y `legible`."""
    ruta = claude_config_dir() / "plugins" / "installed_plugins.json"
    if not ruta.exists():
        return {"instalado": False, "proyectos": [], "legible": True}

    datos = _leer_json(ruta)
    plugins = datos.get("plugins") if isinstance(datos, dict) else None
    if not isinstance(plugins, dict):
        return {"instalado": False, "proyectos": [], "legible": False}

    entradas = plugins.get(PLUGIN) or []
    entradas = [e for e in entradas if isinstance(e, dict)] if isinstance(entradas, list) else []
    return {
        "instalado": any(e.get("scope") == "user" for e in entradas),
        "proyectos": [e.get("projectPath", "?") for e in entradas if e.get("scope") != "user"],
        "legible": True,
    }


def ya_decidio() -> bool:
    """Dijo que no acá, o lo apagó a mano en su config de usuario."""
    if marca_declinado().exists():
        return True
    ajustes = _leer_json(claude_config_dir() / "settings.json")
    habilitados = ajustes.get("enabledPlugins") if isinstance(ajustes, dict) else None
    return isinstance(habilitados, dict) and habilitados.get(PLUGIN) is False


def oferta(proyectos: list[str]) -> str:
    if proyectos:
        situacion = (
            f"`{PLUGIN}` está instalado sólo para {', '.join(proyectos)}: "
            "en cualquier otro repo de esta máquina no rige."
        )
    else:
        situacion = f"`{PLUGIN}` no está instalado en esta máquina."

    return f"""[AWI] {situacion}

`answerable` le da forma fija a las respuestas del agente, para contestarlas con un número en vez de reescribirlas. Las reglas de forma de AWI viven en ese plugin.

Si esta sesión no tiene un operador humano (delegada, `claude -p`), ignorá este aviso.

En tu primera respuesta, además de atender lo que te pidan, ofrecele instalarlo, una sola vez y en su idioma. Aclará que el alcance es de usuario: rige en toda sesión de Claude Code de esta máquina, en cualquier repo.

- Si acepta: `python3 {ESTE_SCRIPT} instalar`
- Si no quiere: `python3 {ESTE_SCRIPT} declinar`. No se le vuelve a ofrecer en esta máquina.
- Si no contesta: no hagas nada. Se le ofrece de nuevo en la próxima sesión.
"""


def comprobar() -> int:
    """El modo hook: imprime la oferta si corresponde, y calla en cualquier otro caso."""
    try:
        estado = instalacion()
        if estado["legible"] and not estado["instalado"] and not ya_decidio():
            print(oferta(estado["proyectos"]))
    except Exception:  # noqa: BLE001 — ver el docstring: no puede romper el arranque
        pass
    return 0


def instalar() -> int:
    claude = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
    pasos = []

    # El nombre puede estar tomado por otra fuente: en la máquina del mantenedor
    # `awi` apunta a un directorio local. Se respeta en vez de pisarlo.
    conocidos = _leer_json(claude_config_dir() / "plugins" / "known_marketplaces.json")
    if not (isinstance(conocidos, dict) and MARKETPLACE in conocidos):
        pasos.append([claude, "plugin", "marketplace", "add", REPO])
    pasos.append([claude, "plugin", "install", PLUGIN, "--scope", "user"])

    salida = []
    for paso in pasos:
        try:
            r = subprocess.run(paso, capture_output=True, text=True, timeout=180)
            salida.append(r.stdout + r.stderr)
        except (OSError, subprocess.TimeoutExpired) as e:
            salida.append(str(e))

    # Lo que manda es el estado que quedó, no el código de salida del CLI.
    if not instalacion()["instalado"]:
        print("".join(salida).strip())
        print(f"\nNo se pudo instalar {PLUGIN}. Adentro de una sesión de Claude Code:")
        print(f"  /plugin marketplace add {REPO}")
        print(f"  /plugin install {PLUGIN}")
        return 1

    marca_declinado().unlink(missing_ok=True)
    print(f"{PLUGIN} instalado con alcance de usuario. Su hook corre desde la próxima sesión.")
    print(f"Para que rija ya en esta sesión, leé {REGLAS} y aplicalo desde este turno.")
    return 0


def declinar() -> int:
    marca = marca_declinado()
    marca.parent.mkdir(parents=True, exist_ok=True)
    marca.touch()
    print(f"No se vuelve a ofrecer {PLUGIN} en esta máquina.")
    print(f"Para instalarlo más adelante: python3 {ESTE_SCRIPT} instalar")
    return 0


def main() -> int:
    accion = sys.argv[1] if len(sys.argv) > 1 else None
    if accion is None:
        return comprobar()
    if accion == "instalar":
        return instalar()
    if accion == "declinar":
        return declinar()
    print(f"Acción desconocida: {accion}. Usá `instalar` o `declinar`.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
