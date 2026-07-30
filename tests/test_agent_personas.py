"""Tests del descubrimiento de personas-agente.

El que importa es `test_el_registro_eliminado_no_hace_falta`: verifica sobre el
árbol real que las claves con las que el registro escrito a mano referenciaba
personas siguen resolviendo. Sin eso, eliminar `employees.json` rompería cada
Agent Brief ya escrito en un issue.

Fixtures propios en `tmp_path` para todo lo demás, siguiendo el patrón de
`tests/test_context_sync.py`: el árbol real es un clon de terceros que puede
cambiar sin aviso, así que atar la mecánica a su contenido sería atarse a algo
que no controlamos.
"""

import pytest

import agent_personas as ap
from paths import AWI_ROOT

#: Claves con las que el registro eliminado referenciaba personas. De sus 35
#: entradas, 33 resuelven desde el árbol y 2 estaban rotas en el registro mismo:
#: `security-engineer` apuntaba a un archivo inexistente, y `nexus-strategy`
#: listaba un playbook sin frontmatter como si fuera un agente. Que un registro
#: escrito a mano tuviera el 6 % de sus entradas muertas es parte del argumento
#: para eliminarlo.
CLAVES_DEL_REGISTRO = (
    "ai-engineer",
    "backend-architect",
    "frontend-developer",
    "devops-automator",
    "rapid-prototyper",
)

arbol_real = pytest.mark.skipif(
    not (AWI_ROOT / ap.AGENCY_RELDIR).is_dir(),
    reason="_system/agency-agents/ no está materializado",
)


def persona(tmp_path, categoria, archivo, frontmatter="name: X\ndescription: hace cosas\n"):
    d = tmp_path / ap.AGENCY_RELDIR / categoria
    d.mkdir(parents=True, exist_ok=True)
    (d / archivo).write_text(f"---\n{frontmatter}---\n\n# cuerpo\n", encoding="utf-8")


# ── Contra el árbol real ──────────────────────────────────────────────────────

@arbol_real
def test_el_registro_eliminado_no_hace_falta():
    """Cada clave del registro sigue resolviendo desde el árbol."""
    for clave in CLAVES_DEL_REGISTRO:
        p = ap.resolver(AWI_ROOT, clave)
        assert (AWI_ROOT / p.ruta).is_file(), f"{clave} resuelve a un archivo inexistente"


@arbol_real
def test_descubre_bastantes_mas_que_las_36_del_registro():
    """El registro era una vista parcial de lo disponible."""
    assert len(ap.descubrir(AWI_ROOT)) > 200


@arbol_real
def test_toda_persona_tiene_tagline_y_categoria():
    for p in ap.descubrir(AWI_ROOT):
        assert p.categoria and p.nombre
        assert p.tagline, f"{p.nombre} no tiene tagline: no se puede rutear"


@arbol_real
def test_los_documentos_del_repo_de_terceros_no_son_personas():
    nombres = {p.nombre for p in ap.descubrir(AWI_ROOT)}
    assert not nombres & {"README", "CONTRIBUTING", "SECURITY", "LICENSE"}


# ── Mecánica, con fixtures propios ────────────────────────────────────────────

def test_el_directorio_es_la_categoria(tmp_path):
    persona(tmp_path, "engineering", "engineering-ai-engineer.md")

    p = ap.descubrir(tmp_path)[0]

    assert p.categoria == "engineering"


def test_el_prefijo_de_categoria_se_saca_del_nombre(tmp_path):
    """`engineering-ai-engineer.md` en `engineering/` es `ai-engineer`: el prefijo
    es redundante con el directorio, y sin sacarlo las referencias ya escritas en
    los Agent Brief dejarían de resolver."""
    persona(tmp_path, "engineering", "engineering-ai-engineer.md")

    assert ap.descubrir(tmp_path)[0].nombre == "ai-engineer"


def test_un_nombre_sin_prefijo_se_conserva(tmp_path):
    persona(tmp_path, "strategy", "planificador.md")

    assert ap.descubrir(tmp_path)[0].nombre == "planificador"


def test_el_description_del_frontmatter_es_el_tagline(tmp_path):
    persona(
        tmp_path, "testing", "testing-api.md",
        frontmatter="name: API\ndescription: Prueba APIs de punta a punta.\ncolor: blue\n",
    )

    assert ap.descubrir(tmp_path)[0].tagline == "Prueba APIs de punta a punta"


def test_un_archivo_sin_frontmatter_no_es_persona(tmp_path):
    """Es cómo el registro eliminado llegó a listar un playbook como agente."""
    d = tmp_path / ap.AGENCY_RELDIR / "strategy"
    d.mkdir(parents=True)
    (d / "playbook.md").write_text("# Un playbook\n\nProsa, no un agente.\n")

    assert ap.descubrir(tmp_path) == []


def test_los_directorios_de_infraestructura_se_ignoran(tmp_path):
    for categoria in (".github", "scripts", "examples"):
        persona(tmp_path, categoria, "algo.md")
    persona(tmp_path, "design", "design-ux.md")

    assert [p.categoria for p in ap.descubrir(tmp_path)] == ["design"]


def test_el_arbol_ausente_falla_ruidosamente(tmp_path):
    """Devolver una lista vacía diría «no hay agentes», que es una respuesta falsa."""
    with pytest.raises(ap.ArbolAusente, match="agency-agents"):
        ap.descubrir(tmp_path)


# ── Resolver y buscar ─────────────────────────────────────────────────────────

def test_resolver_un_nombre_inexistente_nombra_las_parecidas(tmp_path):
    persona(tmp_path, "engineering", "engineering-backend-architect.md")

    with pytest.raises(KeyError, match="backend-architect"):
        ap.resolver(tmp_path, "backend")


def test_buscar_por_categoria_y_por_tagline(tmp_path):
    persona(tmp_path, "security", "security-auditor.md",
            frontmatter="name: A\ndescription: Audita vulnerabilidades.\n")
    persona(tmp_path, "design", "design-ux.md",
            frontmatter="name: B\ndescription: Diseña flujos.\n")

    assert [p.nombre for p in ap.buscar(tmp_path, "security")] == ["auditor"]
    assert [p.nombre for p in ap.buscar(tmp_path, "vulnerab")] == ["auditor"]
    assert [p.nombre for p in ap.buscar(tmp_path, "flujos")] == ["ux"]


def test_el_orden_es_estable(tmp_path):
    for cat, arch in (("testing", "testing-b.md"), ("design", "design-a.md"),
                      ("design", "design-z.md")):
        persona(tmp_path, cat, arch)

    assert [p.nombre for p in ap.descubrir(tmp_path)] == ["a", "z", "b"]


# ── El registro está efectivamente eliminado ──────────────────────────────────

def test_el_registro_ya_no_existe():
    """Un registro obsoleto que todavía se lee es peor que ninguno."""
    assert not (AWI_ROOT / ".claude/reference/employees.json").exists()
