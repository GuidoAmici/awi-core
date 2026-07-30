"""Tests del motor de reglas.

Puros: sin repos, sin git, sin disco (salvo los de carga del archivo de reglas,
que es lo único que toca el disco por diseño).

Los casos de falso positivo son la mitad del valor: un motor que marca cualquier
mención de la palabra «password» convierte el hook en algo que se saltea siempre,
y un hook que se saltea siempre no protege de nada.
"""

import json

import pytest

import sensitive_scan as ss
from paths import AWI_ROOT

REGLAS_REALES = AWI_ROOT / ss.REGLAS_SENSIBLES


@pytest.fixture
def reglas():
    return ss.cargar_reglas(REGLAS_REALES)


def escanear(reglas, ruta, contenido=None):
    return ss.escanear([ss.Entrada(ruta, contenido)], reglas)


def categorias(reporte):
    return {h.categoria for h in reporte.hallazgos}


def nombres(reporte):
    return {h.regla for h in reporte.hallazgos}


# ── Las reglas reales del repo son cargables ──────────────────────────────────

def test_el_archivo_de_reglas_del_repo_carga(reglas):
    """Si esto falla, la auditoría corre a ciegas en CI."""
    assert len(reglas) >= 10
    assert {r.categoria for r in reglas} == set(ss.CATEGORIAS)


# ── Credenciales ──────────────────────────────────────────────────────────────

def test_password_en_claro_dispara_credencial(reglas):
    r = escanear(reglas, "config/app.yaml", 'db_password: "Tr0ub4dor&3xyz"\n')
    assert categorias(r) == {ss.CREDENCIAL}
    assert r.bloqueantes


def test_cadena_de_conexion_dispara_credencial(reglas):
    r = escanear(
        reglas,
        "scripts/migrate.ps1",
        "$url = 'postgresql://postgres:h7Kq2mVt@db.abcdefgh.supabase.co:5432/postgres'\n",
    )
    assert "cadena-de-conexion" in nombres(r)


def test_token_de_proveedor_dispara_credencial(reglas):
    r = escanear(reglas, "notas.md", "usé ghp_" + "a1b2c3d4e5" * 4 + " para probar\n")
    assert "token-de-proveedor" in nombres(r)


def test_clave_privada_dispara_credencial(reglas):
    r = escanear(reglas, "deploy/key", "-----BEGIN OPENSSH PRIVATE KEY-----\nb3Blb\n")
    assert "clave-privada" in nombres(r)


def test_archivo_env_dispara_por_ruta_sin_leer_contenido(reglas):
    """El caso donde el contenido no está disponible: un blob del historial."""
    r = escanear(reglas, "apps/web/.env.local", None)
    assert "archivo-de-entorno" in nombres(r)


def test_env_example_no_dispara(reglas):
    assert not escanear(reglas, "apps/web/.env.example", "API_KEY=\n")


# ── Falsos positivos: la palabra en prosa no es una credencial ────────────────

def test_mencionar_password_en_prosa_no_dispara(reglas):
    prosa = (
        "El operador no debe pegar su password en el repositorio.\n"
        "Cualquier password expuesta se considera comprometida y se rota.\n"
    )
    assert not escanear(reglas, "docs/seguridad.md", prosa)


def test_placeholder_no_dispara(reglas):
    for linea in (
        'api_key: "${DOPPLER_API_KEY}"\n',
        "password = <tu-password-acá>\n",
        'access_token: "YOUR_TOKEN_HERE"\n',
        "SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY\n",
        "password: xxxxxxxxxx\n",
        "client_secret: changeme\n",
    ):
        assert not escanear(reglas, "config/ejemplo.yaml", linea), f"falso positivo: {linea!r}"


def test_leer_del_entorno_no_dispara(reglas):
    """Los tres falsos positivos que la primera corrida sobre el historial real
    encontró: leer un secreto del entorno es justamente lo que se quiere."""
    for linea in (
        'api_key = os.environ.get("ANTHROPIC_API_KEY")\n',
        'const secret = process.env.JWT_SECRET || "secret";\n',
        "password: process.env.TEST_USER_PASSWORD\n",
        'db_password = getenv("DB_PASSWORD")\n',
        "client = anthropic.Anthropic(api_key=api_key)\n",
    ):
        assert not escanear(reglas, "app/config.py", linea), f"falso positivo: {linea!r}"


def test_catalogo_de_patrones_de_terceros_no_dispara(reglas):
    """`_system/agency-agents/` es un clon de terceros cuyos documentos enumeran
    qué buscar. Nombrar un patrón no es tenerlo — el mismo caso que un ADR que
    tiene que poder mencionar «submódulo» al narrar por qué se eliminaron."""
    doc = (
        "# Private key material a detectar\n"
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "Hallazgos típicos: 3 critical, 7 high en una auditoría inicial.\n"
    )
    assert not escanear(reglas, "_system/agency-agents/security/security-senior-secops.md", doc)
    assert escanear(reglas, "docs/otro.md", doc), "fuera de ese árbol sí debe disparar"


def test_cadena_de_conexion_con_placeholder_no_dispara(reglas):
    r = escanear(reglas, "README.md", "postgresql://usuario:password@localhost:5432/db\n")
    assert not r


def test_markdown_normal_no_dispara_nada(reglas):
    doc = (
        "# Notas de la semana\n\n"
        "- Cerré el issue 42 y abrí el 43.\n"
        "- Revisar el informe del lunes: 3 pendientes, 2 en curso.\n"
    )
    assert not escanear(reglas, "_data/notas.md", doc)


# ── Material de cliente ───────────────────────────────────────────────────────

def test_scratch_de_delegado_dispara_por_ruta(reglas):
    r = escanear(reglas, ".claude/tmp/delegates/issue-9/output.log", None)
    assert ss.MATERIAL_DE_CLIENTE in categorias(r)
    assert r.bloqueantes


def test_informe_de_auditoria_dispara_material_de_cliente(reglas):
    """La línea real que abre el log de newhaze-learn en el historial."""
    r = escanear(
        reglas,
        "informes/revision.md",
        "Audit complete: 3 critical, 7 high, 10 medium, 6 low issues found\n",
    )
    assert "informe-de-auditoria" in nombres(r)


def test_volcado_con_filas_dispara_pero_el_esquema_solo_no(reglas):
    con_filas = "CREATE TABLE t (id int);\nINSERT INTO t VALUES (1, 'Cliente SA');\n"
    solo_esquema = "CREATE TABLE t (id int);\nALTER TABLE t ADD COLUMN nombre text;\n"

    assert "volcado-de-datos" in nombres(escanear(reglas, "db/seed.sql", con_filas))
    assert not escanear(reglas, "db/schema.sql", solo_esquema)


# ── Ruido operativo: se reporta pero no bloquea ────────────────────────────────

def test_ruido_operativo_no_bloquea(reglas):
    r = escanear(reglas, "notas/commit_msg.txt", "docs: algo\n")
    assert r.hallazgos
    assert not r.bloqueantes


# ── Severidad y forma del reporte ─────────────────────────────────────────────

def test_la_categoria_gobierna_si_bloquea(reglas):
    entradas = [
        ss.Entrada(".claude/tmp/x.ps1", "echo hola\n"),
        ss.Entrada("viejo.md.bak", "algo\n"),
    ]
    r = ss.escanear(entradas, reglas)
    conteo = r.por_categoria()
    assert conteo[ss.MATERIAL_DE_CLIENTE] == 1
    assert conteo[ss.RUIDO_OPERATIVO] == 1
    assert [h.ruta for h in r.bloqueantes] == [".claude/tmp/x.ps1"]


def test_el_hallazgo_no_reproduce_la_credencial(reglas):
    """La auditoría corre en CI y su salida queda en los logs del workflow."""
    secreto = "Tr0ub4dor&3xyz"
    r = escanear(reglas, "config/app.yaml", f"db_password: {secreto}\n")
    assert r.hallazgos
    for h in r.hallazgos:
        assert secreto not in h.evidencia
        assert secreto not in str(h)
        assert ss.REDACTADO in h.evidencia


def test_el_hallazgo_dice_archivo_regla_y_remedio(reglas):
    """Lo que el hook necesita para que el operador resuelva sin adivinar."""
    r = escanear(reglas, "config/app.yaml", 'password: "Tr0ub4dor3xyz"\n')
    h = r.hallazgos[0]
    assert h.ruta == "config/app.yaml"
    assert h.linea == 1
    assert h.regla and h.remedio
    assert "config/app.yaml:1" in str(h)


def test_una_regla_reporta_una_vez_por_archivo(reglas):
    muchas = "".join(f'password: secreto{i}0000\n' for i in range(50))
    r = escanear(reglas, "config/app.yaml", muchas)
    assert len(r.hallazgos) == 1


def test_reporte_expone_rutas_distintas_para_la_purga(reglas):
    entradas = [
        ss.Entrada(".claude/tmp/a.ps1"),
        ss.Entrada(".claude/tmp/a.ps1"),  # el mismo blob en dos commits
        ss.Entrada(".claude/tmp/b.ps1"),
    ]
    assert ss.escanear(entradas, reglas).rutas() == [".claude/tmp/a.ps1", ".claude/tmp/b.ps1"]


# ── Límites declarados ────────────────────────────────────────────────────────

def test_binario_se_evalua_solo_por_ruta(reglas):
    """Límite explícito: un secreto dentro de un binario no lo ve este motor."""
    binario = "\x00\x01password: Tr0ub4dor3xyz\x00"
    assert not escanear(reglas, "assets/blob.bin", binario)
    assert escanear(reglas, ".claude/tmp/blob.bin", binario), "la ruta sí debe seguir aplicando"


def test_archivo_gigante_se_evalua_solo_por_ruta(reglas):
    gigante = "x" * (ss.MAX_BYTES + 1) + "\npassword: Tr0ub4dor3xyz\n"
    assert not escanear(reglas, "datos/grande.txt", gigante)


# ── Carga de reglas: falla ruidosamente ───────────────────────────────────────

def test_archivo_ausente_falla_en_vez_de_reportar_limpio(tmp_path):
    with pytest.raises(ss.ReglasInvalidas, match="no existe"):
        ss.cargar_reglas(tmp_path / "no-existe.json")


def test_json_invalido_falla(tmp_path):
    f = tmp_path / "r.json"
    f.write_text("{ esto no es json ")
    with pytest.raises(ss.ReglasInvalidas, match="JSON"):
        ss.cargar_reglas(f)


def test_sin_reglas_falla(tmp_path):
    f = tmp_path / "r.json"
    f.write_text(json.dumps({"reglas": []}))
    with pytest.raises(ss.ReglasInvalidas, match="ninguna regla"):
        ss.cargar_reglas(f)


def test_categoria_desconocida_falla_nombrando_las_validas(tmp_path):
    f = tmp_path / "r.json"
    f.write_text(json.dumps({"reglas": [
        {"nombre": "x", "categoria": "grave", "ruta": "^x"}
    ]}))
    with pytest.raises(ss.ReglasInvalidas, match="credencial"):
        ss.cargar_reglas(f)


def test_regla_sin_patron_falla(tmp_path):
    f = tmp_path / "r.json"
    f.write_text(json.dumps({"reglas": [
        {"nombre": "x", "categoria": "credencial"}
    ]}))
    with pytest.raises(ss.ReglasInvalidas, match="ni «ruta» ni «contenido»"):
        ss.cargar_reglas(f)


def test_regex_invalida_falla_nombrando_la_regla(tmp_path):
    f = tmp_path / "r.json"
    f.write_text(json.dumps({"reglas": [
        {"nombre": "rota", "categoria": "credencial", "contenido": "([a-z"}
    ]}))
    with pytest.raises(ss.ReglasInvalidas, match="rota"):
        ss.cargar_reglas(f)


def test_regla_duplicada_falla(tmp_path):
    f = tmp_path / "r.json"
    f.write_text(json.dumps({"reglas": [
        {"nombre": "x", "categoria": "credencial", "ruta": "^a"},
        {"nombre": "x", "categoria": "credencial", "ruta": "^b"},
    ]}))
    with pytest.raises(ss.ReglasInvalidas, match="duplicada"):
        ss.cargar_reglas(f)


# ── El motor es puro ──────────────────────────────────────────────────────────

def test_el_motor_no_conoce_git(reglas):
    """El corte del PRD, aseverado. Si alguien importa subprocess acá, se rompe."""
    fuente = (AWI_ROOT / ".claude/skills/shared/scripts/sensitive_scan.py").read_text()
    imports = [l for l in fuente.splitlines() if l.startswith(("import ", "from "))]
    assert not [l for l in imports if "subprocess" in l or "git" in l], imports
