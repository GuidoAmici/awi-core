"""Tests del registro de invocaciones.

El que importa es `test_un_registro_corrupto_no_tumba_la_skill_que_lo_llama`: el
registro es telemetría, y la telemetría nunca puede romper la función que
instrumenta. Un `/today` que falla porque su log tiene una línea a medias es peor
que no tener log.
"""

import json

import pytest

import log_command as lc
from paths import AWI_ROOT

HOOK = AWI_ROOT / ".claude/hooks/log-skill-use.py"


@pytest.fixture
def registro(tmp_path, monkeypatch):
    """Un registro aislado: los tests no escriben en el del operador."""
    users = tmp_path / "_data/users"
    (users / "42481462").mkdir(parents=True)
    (users / "current-user.json").write_text(json.dumps({"github-id": "42481462", "login": "t"}))
    monkeypatch.setattr(lc, "USERS_DIR", users)
    monkeypatch.setattr(lc, "CURRENT_USER_FILE", users / "current-user.json")
    return users / "42481462" / lc.ARCHIVO


# ── Registrar ─────────────────────────────────────────────────────────────────

def test_registra_una_linea(registro):
    assert lc.registrar("today", "invoked", fuente="prompt")

    entradas = lc.leer(registro)
    assert len(entradas) == 1
    assert entradas[0]["command"] == "today"
    assert entradas[0]["outcome"] == "invoked"
    assert entradas[0]["fuente"] == "prompt"


def test_registra_tambien_las_fallidas(registro):
    """Distinguir «no se usa» de «se intenta y falla»."""
    lc.registrar("awi-org", "errored")
    lc.registrar("awi-org", "completed")

    resultados = [e["outcome"] for e in lc.leer(registro)]
    assert resultados == ["errored", "completed"]


def test_la_fuente_distingue_el_hook_de_la_skill(registro):
    """Es lo que permite medir cuánto subcontaba el registro anterior."""
    lc.registrar("today", "invoked", fuente="prompt")
    lc.registrar("today", "completed", fuente="skill")

    fuentes = {e["fuente"] for e in lc.leer(registro)}
    assert fuentes == {"prompt", "skill"}


def test_el_conteo_ordena_de_mas_a_menos(registro):
    for _ in range(3):
        lc.registrar("today", "invoked")
    lc.registrar("week", "invoked")

    assert list(lc.conteo(registro)) == ["today", "week"]
    assert lc.conteo(registro)["today"] == 3


# ── La telemetría nunca rompe lo que instrumenta ──────────────────────────────

def test_un_registro_corrupto_no_tumba_la_skill_que_lo_llama(registro):
    """El caso que el PRD nombra: un write interrumpido deja una línea a medias."""
    registro.parent.mkdir(parents=True, exist_ok=True)
    registro.write_text('{"command": "today", "outcome": "invoked"}\n{"command": "week", "out\n')

    entradas = lc.leer(registro)

    assert len(entradas) == 1, "la línea buena se conserva, la corrupta se saltea"
    assert entradas[0]["command"] == "today"
    assert lc.registrar("quarter", "invoked"), "y se puede seguir escribiendo"


def test_sin_usuario_logueado_no_levanta(tmp_path, monkeypatch):
    monkeypatch.setattr(lc, "CURRENT_USER_FILE", tmp_path / "no-existe.json")

    assert lc.registrar("today", "invoked") is False


def test_un_destino_no_escribible_no_levanta(tmp_path, monkeypatch):
    ocupado = tmp_path / "archivo"
    ocupado.write_text("no soy un directorio")
    monkeypatch.setattr(lc, "USERS_DIR", ocupado)
    monkeypatch.setattr(lc, "CURRENT_USER_FILE", tmp_path / "cu.json")
    (tmp_path / "cu.json").write_text(json.dumps({"github-id": "1", "login": "t"}))

    assert lc.registrar("today", "invoked") is False


def test_leer_un_registro_inexistente_devuelve_vacio(tmp_path):
    assert lc.leer(tmp_path / "no-existe.jsonl") == []


# ── El hook: de instrucción a código ──────────────────────────────────────────

def cargar_hook():
    import importlib.util

    spec = importlib.util.spec_from_file_location("log_skill_use", HOOK)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_el_hook_reconoce_una_invocacion_de_skill():
    hook = cargar_hook()

    assert hook.skill_invocada("/today") == "today"
    assert hook.skill_invocada("/awi-org newhaze") == "awi-org"
    assert hook.skill_invocada("  /week-review  ") == "week-review"
    assert hook.skill_invocada("/code-review ultra 42") == "code-review"
    assert hook.skill_invocada("/plugin:skill algo") == "plugin:skill"


def test_el_hook_no_confunde_prosa_con_una_skill():
    hook = cargar_hook()

    assert hook.skill_invocada("hola, arreglá el bug") is None
    assert hook.skill_invocada("mirá en src/x.py o /etc/hosts") is None
    assert hook.skill_invocada("") is None
    assert hook.skill_invocada("el ratio es 3/4") is None


def test_el_hook_existe_y_esta_registrado_en_settings():
    """Sin el registro en settings.json, el hook no corre y el registro sigue
    dependiendo de que el agente se acuerde."""
    assert HOOK.is_file()

    settings = json.loads((AWI_ROOT / ".claude/settings.json").read_text())
    comandos = [
        h.get("command", "")
        for entrada in settings["hooks"].get("UserPromptSubmit", [])
        for h in entrada.get("hooks", [])
    ]
    assert any("log-skill-use" in c for c in comandos), comandos


def test_el_hook_no_rompe_el_prompt_ante_una_entrada_invalida():
    """Cualquier error tiene que tragarse: sale con 0 y el prompt sigue."""
    import subprocess
    import sys

    for entrada in ("basura no json", "", "[]", '{"otra": "cosa"}'):
        r = subprocess.run(
            [sys.executable, str(HOOK)], input=entrada, capture_output=True, text=True
        )
        assert r.returncode == 0, f"falló con {entrada!r}: {r.stderr}"
