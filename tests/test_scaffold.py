"""Tests del scaffolding y del toggle.

El scaffolding no tenía ningún test, y es lo que crea la estructura de una
organización nueva: es el punto de mayor rendimiento del PRD 4.

Los dos que importan son `test_es_idempotente` —correrlo dos veces no rompe ni
duplica, que es exactamente cuando alguien lo vuelve a correr: después de que se
cortó a mitad de camino— y `test_toggle_descubre_por_manifiesto_y_no_por_gitmodules`,
la regresión de los tres `toggle_client.py` que leían un registro eliminado hace
dos ADRs.
"""

import json
import subprocess
from pathlib import Path

import pytest

import scaffold
import toggle_repo as tr


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    assert r.returncode == 0, f"git {' '.join(args)} falló: {r.stderr}"
    return r


# ── Scaffolding ───────────────────────────────────────────────────────────────

def test_crea_la_estructura_esperada(tmp_path):
    r = scaffold.crear_arbol("newhaze", tmp_path)

    assert r.creado
    for folder in scaffold.AGENDA_FOLDERS:
        assert (r.path / "agenda" / folder).is_dir(), folder
    assert (r.path / "documentation").is_dir()
    assert (r.path / "codebase").is_dir()
    assert (r.path / "CLAUDE.md").is_file()
    assert (r.path / ".gitignore").is_file()
    assert (r.path / "codebases.json").is_file()


def test_inicializa_el_repo_con_su_primer_commit(tmp_path):
    r = scaffold.crear_arbol("newhaze", tmp_path)

    assert (r.path / ".git").is_dir()
    assert git(r.path, "rev-list", "--count", "HEAD").stdout.strip() == "1"
    assert not git(r.path, "status", "--porcelain").stdout.strip()


def test_es_idempotente(tmp_path):
    """Correrlo dos veces no rompe ni duplica. Es cuando alguien lo vuelve a
    correr: después de que se cortó a mitad de camino."""
    primera = scaffold.crear_arbol("newhaze", tmp_path)
    commits_antes = git(primera.path, "rev-list", "--count", "HEAD").stdout.strip()

    segunda = scaffold.crear_arbol("newhaze", tmp_path)

    assert not segunda.creado
    assert segunda.path == primera.path
    assert git(primera.path, "rev-list", "--count", "HEAD").stdout.strip() == commits_antes
    assert not git(primera.path, "status", "--porcelain").stdout.strip()
    assert "no se tocó nada" in " ".join(segunda.acciones)


def test_completa_un_scaffolding_a_medias(tmp_path):
    """El caso que hace útil la idempotencia."""
    r = scaffold.crear_arbol("newhaze", tmp_path)
    (r.path / "codebases.json").unlink()
    (r.path / "agenda" / "tasks").rmdir()

    segunda = scaffold.crear_arbol("newhaze", tmp_path)

    assert (segunda.path / "codebases.json").is_file()
    assert (segunda.path / "agenda" / "tasks").is_dir()
    assert any("codebases.json" in a for a in segunda.acciones)


def test_no_pisa_un_archivo_editado(tmp_path):
    """Un CLAUDE.md que el operador tocó no se sobreescribe."""
    r = scaffold.crear_arbol("newhaze", tmp_path)
    (r.path / "CLAUDE.md").write_text("# lo edité yo\n")

    scaffold.crear_arbol("newhaze", tmp_path)

    assert (r.path / "CLAUDE.md").read_text() == "# lo edité yo\n"


def test_el_gitignore_protege_de_tragarse_los_codebases(tmp_path):
    """Requisito de corrección, no higiene: sin esto `git add -A` los embebe."""
    r = scaffold.crear_arbol("newhaze", tmp_path)

    assert "codebase/*/" in (r.path / ".gitignore").read_text()


def test_el_codebases_json_arranca_vacio_y_es_json(tmp_path):
    r = scaffold.crear_arbol("newhaze", tmp_path)

    datos = json.loads((r.path / "codebases.json").read_text())

    assert datos["codebases"] == {}
    assert "_comment" in datos


def test_el_titulo_del_claude_md_sale_del_nombre(tmp_path):
    r = scaffold.crear_arbol("acme-corp", tmp_path)

    assert "Acme Corp" in (r.path / "CLAUDE.md").read_text()


# ── Registro en el manifiesto ─────────────────────────────────────────────────

def manifiesto(tmp_path, contenido=None):
    f = tmp_path / "user-submodules.json"
    f.write_text(json.dumps(contenido if contenido is not None else {"submodules": {}}))
    return f


def test_registrar_agrega_la_entrada(tmp_path):
    m = manifiesto(tmp_path)

    assert scaffold.registrar("newhaze", "https://github.com/x/newhaze.git", m)

    entrada = json.loads(m.read_text())["submodules"]["newhaze"]
    assert entrada["url"] == "https://github.com/x/newhaze.git"
    assert entrada["path"].endswith("newhaze")
    assert entrada["active"] is True
    assert entrada["type"] == "org-workspace"


def test_registrar_es_idempotente(tmp_path):
    m = manifiesto(tmp_path)
    scaffold.registrar("newhaze", "https://github.com/x/newhaze.git", m)

    assert not scaffold.registrar("newhaze", "https://github.com/x/otra.git", m)

    entradas = json.loads(m.read_text())["submodules"]
    assert len(entradas) == 1
    assert entradas["newhaze"]["url"].endswith("newhaze.git"), "no debe pisar la url"


def test_registrar_sin_manifiesto_falla_diciendo_qué_hacer(tmp_path):
    with pytest.raises(scaffold.ScaffoldFallido, match="awi-user"):
        scaffold.registrar("x", "url", tmp_path / "no-existe.json")


def test_scaffold_sin_url_crea_pero_no_registra(tmp_path):
    """Crear el árbol sin remoto es legítimo: el repo de GitHub puede no existir."""
    r = scaffold.scaffold("newhaze", tmp_path)

    assert r.creado
    assert not r.registrado
    assert "ninguna" in scaffold.describir(r, "newhaze") or "Todavía no está" in scaffold.describir(r, "newhaze")


def test_scaffold_con_url_hace_las_dos_cosas(tmp_path):
    m = manifiesto(tmp_path)

    r = scaffold.scaffold("newhaze", tmp_path / "orgs", "https://github.com/x/n.git", m)

    assert r.creado and r.registrado
    assert "newhaze" in json.loads(m.read_text())["submodules"]


# ── Toggle por manifiesto ─────────────────────────────────────────────────────

@pytest.fixture
def instancia(tmp_path):
    """Una raíz de AWI con un operador logueado y un manifiesto con dos orgs."""
    raiz = tmp_path / "awi"
    (raiz / "_data/users/42481462").mkdir(parents=True)
    (raiz / "_data/users/current-user.json").write_text(json.dumps({
        "github-id": "42481462", "login": "test",
    }))
    (raiz / "_data/users/42481462/user-submodules.json").write_text(json.dumps({
        "submodules": {
            "newhaze": {
                "url": "https://github.com/x/newhaze.git",
                "path": "_data/organizations/newhaze",
                "branch": "main", "type": "org-workspace", "active": True,
                "codebases": {
                    "newhaze-learn": {"active": True},
                    "newhaze-web": {"active": False},
                },
            },
            "afin": {
                "url": "https://github.com/x/afin.git",
                "path": "_data/organizations/afin",
                "branch": "main", "type": "org-workspace", "active": False,
            },
        }
    }))
    return raiz


def test_toggle_descubre_por_manifiesto_y_no_por_gitmodules(instancia):
    """La regresión. Los tres toggle_client.py corrían `git submodule status` y
    fallaban con «no registrado en .gitmodules» — un archivo eliminado hace dos
    ADRs. Acá no hay ningún repo de git y el descubrimiento funciona igual."""
    assert not (instancia / ".gitmodules").exists()
    assert not (instancia / ".git").exists()

    claves = {e.clave for e in tr.listar(instancia)}

    assert claves == {"newhaze", "afin", "newhaze/newhaze-learn", "newhaze/newhaze-web"}


def test_el_estado_sale_del_manifiesto(instancia):
    por_clave = {e.clave: e for e in tr.listar(instancia)}

    assert por_clave["newhaze"].activo
    assert not por_clave["afin"].activo
    assert por_clave["newhaze/newhaze-learn"].activo
    assert not por_clave["newhaze/newhaze-web"].activo


def test_activar_una_org_lo_refleja_en_el_manifiesto(instancia):
    e = tr.togglear(instancia, "afin", True)

    assert e.activo
    datos = json.loads((instancia / "_data/users/42481462/user-submodules.json").read_text())
    assert datos["submodules"]["afin"]["active"] is True


def test_desactivar_un_codebase_lo_refleja_en_el_manifiesto(instancia):
    """Lo que antes fallaba contra un registro eliminado."""
    e = tr.togglear(instancia, "newhaze/newhaze-learn", False)

    assert not e.activo
    datos = json.loads((instancia / "_data/users/42481462/user-submodules.json").read_text())
    assert datos["submodules"]["newhaze"]["codebases"]["newhaze-learn"]["active"] is False


def test_un_codebase_se_resuelve_por_nombre_si_no_es_ambiguo(instancia):
    e = tr.togglear(instancia, "newhaze-web", True)

    assert e.clave == "newhaze/newhaze-web"
    assert e.activo


def test_un_nombre_inexistente_lista_las_opciones_validas(instancia):
    """Un error de git no le dice nada a alguien que por diseño no usa git."""
    with pytest.raises(tr.RepoDesconocido) as e:
        tr.togglear(instancia, "el-del-lunes", True)

    mensaje = e.value.args[0]
    assert "newhaze" in mensaje and "afin" in mensaje
    assert "submodule" not in mensaje, "no puede hablar de un mecanismo eliminado"


def test_un_nombre_ambiguo_pide_la_forma_completa(instancia):
    datos_path = instancia / "_data/users/42481462/user-submodules.json"
    datos = json.loads(datos_path.read_text())
    datos["submodules"]["afin"]["codebases"] = {"newhaze-learn": {"active": True}}
    datos_path.write_text(json.dumps(datos))

    with pytest.raises(tr.RepoDesconocido, match="ambiguo"):
        tr.togglear(instancia, "newhaze-learn", False)


def test_desactivar_no_borra_el_directorio(instancia):
    destino = instancia / "_data/organizations/newhaze"
    destino.mkdir(parents=True)
    (destino / "importante.md").write_text("mi trabajo\n")

    tr.togglear(instancia, "newhaze", False)

    assert (destino / "importante.md").read_text() == "mi trabajo\n"


def test_el_status_dice_si_esta_materializado(instancia):
    (instancia / "_data/organizations/newhaze").mkdir(parents=True)
    (instancia / "_data/organizations/newhaze/algo.md").write_text("x")

    por_clave = {e.clave: e for e in tr.listar(instancia)}

    assert por_clave["newhaze"].materializado
    assert not por_clave["afin"].materializado


def test_el_cli_sale_con_1_ante_un_nombre_desconocido(instancia, capsys):
    assert tr.main(["enable", "inexistente", "--raiz", str(instancia)]) == 1
    assert "no declara" in capsys.readouterr().err


def test_el_cli_muestra_el_status(instancia, capsys):
    assert tr.main(["status", "--raiz", str(instancia)]) == 0
    salida = capsys.readouterr().out
    assert "newhaze" in salida and "afin" in salida


# ── Ya no hay cuatro copias ───────────────────────────────────────────────────

def test_no_quedan_scripts_de_scaffolding_duplicados():
    """La condición del PRD: un arreglo se aplica una vez, no cuatro."""
    from paths import AWI_ROOT

    copias = list(AWI_ROOT.glob(".claude/skills/*/scripts/init_client.py"))
    copias += list(AWI_ROOT.glob(".claude/skills/*/scripts/init_workspace.py"))
    copias += list(AWI_ROOT.glob(".claude/skills/*/scripts/toggle_client.py"))

    assert not copias, f"volvieron las copias: {[str(c) for c in copias]}"


def test_las_skills_retiradas_no_estan():
    from paths import AWI_ROOT

    for retirada in ("awi-client", "new-client", "initialize"):
        assert not (AWI_ROOT / ".claude/skills" / retirada / "SKILL.md").exists(), retirada


def test_la_skill_que_queda_usa_el_modulo_compartido():
    from paths import AWI_ROOT

    fuente = (AWI_ROOT / ".claude/skills/awi-org/scripts/init_org.py").read_text()

    assert "import scaffold" in fuente
    assert "AGENDA_FOLDERS" not in fuente, "volvió a tener la mecánica adentro"
