"""La oferta de `answerable`: cuándo se hace, cuándo se calla y qué deja `instalar`."""
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

from paths import AWI_ROOT

HOOK = AWI_ROOT / ".claude/hooks/check-answerable.py"
PLUGIN = "answerable@awi"


def _cargar():
    spec = importlib.util.spec_from_file_location("check_answerable", HOOK)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


hook = _cargar()


@pytest.fixture
def config(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path))
    return tmp_path


def instalados(config: Path, *entradas: dict, version: int = 2) -> None:
    (config / "plugins").mkdir(exist_ok=True)
    (config / "plugins/installed_plugins.json").write_text(
        json.dumps({"version": version, "plugins": {PLUGIN: list(entradas)}})
    )


def test_ofrece_en_una_config_vacia(config, capsys):
    assert hook.comprobar() == 0
    salida = capsys.readouterr().out
    assert "no está instalado" in salida
    assert "instalar" in salida and "declinar" in salida


def test_calla_si_esta_instalado_para_el_usuario(config, capsys):
    instalados(config, {"scope": "user"})
    hook.comprobar()
    assert capsys.readouterr().out == ""


def test_una_instalacion_de_proyecto_no_alcanza_y_lo_dice(config, capsys):
    instalados(config, {"scope": "project", "projectPath": "/repos/awi"})
    hook.comprobar()
    salida = capsys.readouterr().out
    assert "sólo para /repos/awi" in salida


def test_calla_si_declino(config, capsys):
    hook.declinar()
    capsys.readouterr()
    hook.comprobar()
    assert capsys.readouterr().out == ""


def test_calla_si_lo_apago_en_su_config_de_usuario(config, capsys):
    (config / "settings.json").write_text(json.dumps({"enabledPlugins": {PLUGIN: False}}))
    hook.comprobar()
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("contenido", ["no es json", "[]", '{"plugins": []}', "{}"])
def test_calla_si_no_reconoce_el_formato(config, capsys, contenido):
    (config / "plugins").mkdir()
    (config / "plugins/installed_plugins.json").write_text(contenido)
    assert hook.comprobar() == 0
    assert capsys.readouterr().out == ""


def test_un_settings_roto_no_impide_ofrecer(config, capsys):
    (config / "settings.json").write_text("{ roto")
    assert hook.comprobar() == 0
    assert "no está instalado" in capsys.readouterr().out


def _cli_falso(config: Path, llamadas: list, instala: bool = True):
    def correr(comando, **_):
        llamadas.append(comando[1:])
        if instala and comando[2] == "install":
            instalados(config, {"scope": "user"})
        return subprocess.CompletedProcess(comando, 0, "", "")

    return correr


def test_instalar_agrega_el_marketplace_y_borra_el_no_anterior(config, monkeypatch, capsys):
    hook.declinar()
    llamadas = []
    monkeypatch.setattr(hook.subprocess, "run", _cli_falso(config, llamadas))

    assert hook.instalar() == 0
    assert llamadas == [
        ["plugin", "marketplace", "add", "GuidoAmici/awi-core"],
        ["plugin", "install", PLUGIN, "--scope", "user"],
    ]
    assert not hook.marca_declinado().exists()
    capsys.readouterr()
    hook.comprobar()
    assert capsys.readouterr().out == ""


def test_instalar_respeta_un_marketplace_awi_que_ya_existe(config, monkeypatch):
    (config / "plugins").mkdir()
    (config / "plugins/known_marketplaces.json").write_text(
        json.dumps({"awi": {"source": {"source": "directory", "path": "/local"}}})
    )
    llamadas = []
    monkeypatch.setattr(hook.subprocess, "run", _cli_falso(config, llamadas))

    assert hook.instalar() == 0
    assert llamadas == [["plugin", "install", PLUGIN, "--scope", "user"]]


def test_instalar_juzga_por_el_estado_final_y_no_por_el_codigo_de_salida(config, monkeypatch, capsys):
    llamadas = []
    monkeypatch.setattr(hook.subprocess, "run", _cli_falso(config, llamadas, instala=False))

    assert hook.instalar() == 1
    assert "/plugin install answerable@awi" in capsys.readouterr().out


def test_el_hook_corre_solo_al_abrir_la_sesion():
    ajustes = json.loads((AWI_ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
    entradas = [
        e
        for e in ajustes["hooks"]["SessionStart"]
        if any("check-answerable.py" in h["command"] for h in e["hooks"])
    ]
    assert [e["matcher"] for e in entradas] == ["startup"]
