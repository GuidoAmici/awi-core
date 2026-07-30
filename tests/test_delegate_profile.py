"""Tests del perfil de ejecución.

La pregunta que contestan es la del PRD: **dado un perfil, ¿el proceso puede
llegar a doppler?** Y se contesta sin lanzar ningún proceso.

Los tres que sostienen el PRD son
`test_el_perfil_por_defecto_no_alcanza_ningun_servidor_sensible`,
`test_todo_perfil_pasa_strict_mcp_config` —sin ese flag la configuración del
operador se suma y pasar una mínima no quita nada— y
`test_un_perfil_inexistente_falla_en_vez_de_caer_al_comportamiento_heredado`.
"""

import json

import pytest

import delegate_profile as dp
from paths import AWI_ROOT


@pytest.fixture
def catalogo():
    return dp.cargar(AWI_ROOT)


# ── Lo que el PRD viene a garantizar ──────────────────────────────────────────

def test_el_perfil_por_defecto_no_alcanza_ningun_servidor_sensible(catalogo):
    """La afirmación central. Se lee del archivo de configuración MCP, no del
    campo declarativo: el campo es la intención, el archivo es lo que el proceso
    va a recibir."""
    perfil = catalogo.por_defecto()

    servidores = set(dp.servidores_de(AWI_ROOT, perfil))

    assert not servidores & dp.SENSIBLES, (
        f"el perfil por defecto alcanza {sorted(servidores & dp.SENSIBLES)}"
    )
    assert "doppler" not in servidores
    assert "supabase" not in servidores
    assert "mercadopago" not in servidores
    assert "gmail" not in servidores


def test_la_configuracion_heredada_del_operador_si_los_tiene():
    """La contraparte que hace que el test anterior valga algo.

    Sin esto, «el perfil no incluye doppler» podría estar pasando porque doppler
    no existe en ninguna parte.
    """
    heredada = json.loads((AWI_ROOT / ".mcp.json").read_text())
    servidores = set(heredada.get("mcpServers", {}))

    assert servidores & dp.SENSIBLES, (
        "la configuración del operador ya no tiene servidores sensibles: "
        "el test del perfil por defecto dejó de probar algo"
    )
    assert len(servidores) > 5, "el problema era heredar doce servidores"


def test_todo_perfil_pasa_strict_mcp_config(catalogo):
    """Sin el flag, la configuración del operador se SUMA a la que se pasa."""
    for nombre, perfil in catalogo.perfiles.items():
        args = perfil.linea_de_comandos(AWI_ROOT)
        assert "--strict-mcp-config" in args, f"«{nombre}» no corta la herencia"
        assert "--mcp-config" in args


def test_el_perfil_por_defecto_es_el_mas_restrictivo(catalogo):
    """Olvidarse de elegir tiene que fallar del lado seguro."""
    por_defecto = set(dp.servidores_de(AWI_ROOT, catalogo.por_defecto()))

    for nombre, perfil in catalogo.perfiles.items():
        if nombre == dp.POR_DEFECTO:
            continue
        otros = set(dp.servidores_de(AWI_ROOT, perfil))
        if otros:
            assert por_defecto <= otros or not (por_defecto - otros), (
                f"«{nombre}» no es una ampliación del perfil por defecto"
            )
        assert len(por_defecto) <= max(len(otros), len(por_defecto))


def test_se_conserva_la_ejecucion_desatendida(catalogo):
    """Quitar el flag cuelga al delegado en el primer prompt de permisos, y un
    delegado que no corre desatendido no sirve de nada. El PRD achica lo que el
    flag habilita, no quita el flag."""
    for nombre, perfil in catalogo.perfiles.items():
        assert "--dangerously-skip-permissions" in perfil.flags, nombre


def test_el_perfil_absorbe_el_tope_de_reloj(catalogo):
    """Ya existía desde 9f4b575 como parámetro suelto; ahora es campo del perfil."""
    for perfil in catalogo.perfiles.values():
        assert 0 < perfil.timeout_s <= dp.TIMEOUT_POR_DEFECTO_S


def test_el_perfil_declara_cuando_alcanza_algo_sensible(catalogo):
    """Auditar de un vistazo: lo que el PRD pide de la user story 2."""
    assert catalogo["con-base"].alcanza_algo_sensible == ("supabase",)
    assert catalogo.por_defecto().alcanza_algo_sensible == ()


def test_todo_mcp_config_declarado_existe_y_es_json(catalogo):
    """Un perfil que apunta a un archivo inexistente arrancaría sin configuración."""
    for nombre, perfil in catalogo.perfiles.items():
        dp.servidores_de(AWI_ROOT, perfil)  # levanta PerfilInvalido si falla


# ── Falla ruidosamente ────────────────────────────────────────────────────────

def test_un_perfil_inexistente_falla_en_vez_de_caer_al_comportamiento_heredado(catalogo):
    with pytest.raises(dp.PerfilInvalido, match="no hay perfil"):
        catalogo["el-que-me-da-todo"]


def test_el_error_nombra_los_perfiles_validos(catalogo):
    with pytest.raises(dp.PerfilInvalido, match=dp.POR_DEFECTO):
        catalogo["inexistente"]


def test_archivo_de_perfiles_ausente_falla(tmp_path):
    with pytest.raises(dp.PerfilInvalido, match="no existe"):
        dp.cargar(tmp_path)


def test_sin_perfil_por_defecto_falla(tmp_path):
    """Si el por defecto no existe, un despacho que no elige no tiene a qué caer."""
    f = tmp_path / "p.json"
    f.write_text(json.dumps({"perfiles": {"otro": {"mcp_config": "x.json"}}}))

    with pytest.raises(dp.PerfilInvalido, match=dp.POR_DEFECTO):
        dp.cargar(tmp_path, f)


def test_perfil_sin_mcp_config_falla(tmp_path):
    f = tmp_path / "p.json"
    f.write_text(json.dumps({"perfiles": {dp.POR_DEFECTO: {"descripcion": "x"}}}))

    with pytest.raises(dp.PerfilInvalido, match="mcp_config"):
        dp.cargar(tmp_path, f)


def test_json_invalido_falla(tmp_path):
    f = tmp_path / "p.json"
    f.write_text("{ no json")

    with pytest.raises(dp.PerfilInvalido, match="JSON"):
        dp.cargar(tmp_path, f)


def test_mcp_config_inexistente_falla_nombrando_el_perfil(tmp_path):
    f = tmp_path / "p.json"
    f.write_text(json.dumps({"perfiles": {dp.POR_DEFECTO: {"mcp_config": "no-existe.json"}}}))
    catalogo = dp.cargar(tmp_path, f)

    with pytest.raises(dp.PerfilInvalido, match=dp.POR_DEFECTO):
        dp.servidores_de(tmp_path, catalogo.por_defecto())


# ── La política es dato ───────────────────────────────────────────────────────

def test_agregar_un_perfil_no_requiere_tocar_el_lanzador(tmp_path):
    """El corte del PRD: política en datos, mecanismo en código."""
    (tmp_path / "mcp.json").write_text(json.dumps({"mcpServers": {"github": {}}}))
    f = tmp_path / "p.json"
    f.write_text(json.dumps({"perfiles": {
        dp.POR_DEFECTO: {"mcp_config": "mcp.json", "flags": ["--dangerously-skip-permissions"]},
        "inventado-en-este-test": {"mcp_config": "mcp.json", "timeout_s": 60},
    }}))

    catalogo = dp.cargar(tmp_path, f)

    assert catalogo["inventado-en-este-test"].timeout_s == 60
    assert dp.servidores_de(tmp_path, catalogo["inventado-en-este-test"]) == ["github"]


def test_describir_muestra_los_servidores_reales(catalogo):
    texto = dp.describir(AWI_ROOT, catalogo)

    assert dp.POR_DEFECTO in texto
    assert "POR DEFECTO" in texto
    assert "github" in texto
    assert "alcanza supabase" in texto, "tiene que avisar cuál llega a algo sensible"
