"""Tests de la auditoría del historial.

El que importa es `test_encuentra_lo_que_ya_no_esta_en_head`: es exactamente la
situación de awi-core. Los objetos de `.claude/tmp/` salieron del árbol en
8334bed y siguen en el historial de un repo público, así que una auditoría que
sólo mira `HEAD` reporta «todo limpio» sobre el problema entero.

Siguen el patrón de `tests/test_context_sync.py`: repos reales en `tmp_path`, con
un helper `git()` que asevera el código de salida.
"""

import json
import subprocess
from pathlib import Path

import pytest

import history_audit as ha
import sensitive_scan as ss
from paths import AWI_ROOT


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    assert r.returncode == 0, f"git {' '.join(args)} falló: {r.stderr}"
    return r


@pytest.fixture
def reglas():
    return ss.cargar_reglas(AWI_ROOT / ss.REGLAS_SENSIBLES)


def repo_limpio(tmp_path: Path, nombre: str = "repo") -> Path:
    repo = tmp_path / nombre
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@t")
    git(repo, "config", "user.name", "T")
    (repo / "README.md").write_text("# proyecto\n\nNada sensible acá.\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "inicial")
    return repo


def ensuciar(repo: Path) -> None:
    """Planta el material y después lo saca del árbol — el escenario real."""
    tmp = repo / ".claude/tmp/delegates/issue-9"
    tmp.mkdir(parents=True)
    (tmp / "output.log").write_text(
        "Auditoría del código del cliente\n3 critical, 7 high, 10 medium issues found\n"
    )
    (tmp / "status.json").write_text(json.dumps({"estado": "done"}))
    (repo / ".claude/tmp/migrar.ps1").write_text(
        '$key = "sbp_' + "a1b2c3d4" * 5 + '"\n'
    )
    git(repo, "add", "-Af")
    git(repo, "commit", "-qm", "scratch del delegado")

    git(repo, "rm", "-r", "-q", "--cached", ".claude/tmp")
    (repo / ".gitignore").write_text(".claude/tmp/\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "desversionar el scratch")


# ── El caso que da razón de ser a la auditoría ────────────────────────────────

def test_encuentra_lo_que_ya_no_esta_en_head(tmp_path, reglas):
    repo = repo_limpio(tmp_path)
    ensuciar(repo)

    assert not (repo / ".claude/tmp").exists() or not git(
        repo, "ls-files", ".claude/tmp"
    ).stdout, "el material tiene que estar fuera del árbol para que el test valga"

    reporte = ha.auditar(repo, reglas)

    rutas = reporte.rutas()
    assert ".claude/tmp/delegates/issue-9/output.log" in rutas
    assert ".claude/tmp/migrar.ps1" in rutas
    assert reporte.bloqueantes


def test_auditar_solo_head_no_lo_ve(tmp_path, reglas):
    """La contraparte: por qué el recorrido tiene que ser del historial completo."""
    repo = repo_limpio(tmp_path)
    ensuciar(repo)

    solo_head = ha.auditar(repo, reglas, refs=("HEAD^{tree}",))

    assert not solo_head.hallazgos


def test_repo_limpio_no_reporta_nada(tmp_path, reglas):
    assert not ha.auditar(repo_limpio(tmp_path), reglas).hallazgos


def test_reporta_conteo_por_categoria(tmp_path, reglas):
    repo = repo_limpio(tmp_path)
    ensuciar(repo)

    conteo = ha.auditar(repo, reglas).por_categoria()

    assert conteo[ss.MATERIAL_DE_CLIENTE] >= 3
    assert conteo[ss.CREDENCIAL] >= 1


def test_encuentra_material_en_una_rama_no_mergeada(tmp_path, reglas):
    """`--all` y no `HEAD`: una rama abandonada sigue publicando lo que tiene."""
    repo = repo_limpio(tmp_path)
    git(repo, "checkout", "-q", "-b", "experimento")
    (repo / ".env").write_text("SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiJ9.abcdefghijkl.mnopqrstuvwx\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "prueba local")
    git(repo, "checkout", "-q", "main")

    reporte = ha.auditar(repo, reglas)

    assert ".env" in reporte.rutas()


def test_el_reporte_incluye_el_limite_de_la_purga(tmp_path, reglas):
    """Un reporte vacío sin esta advertencia se lee como «ya no existe»."""
    repo = repo_limpio(tmp_path)
    texto = ha.formatear(ha.auditar(repo, reglas), repo)
    assert "NO garantiza borrado en GitHub" in texto
    assert "se rota" in texto

    ensuciar(repo)
    con_hallazgos = ha.formatear(ha.auditar(repo, reglas), repo)
    assert "NO garantiza borrado en GitHub" in con_hallazgos


def test_salida_json_es_parseable_y_trae_las_rutas(tmp_path, reglas):
    repo = repo_limpio(tmp_path)
    ensuciar(repo)

    datos = json.loads(ha.como_json(ha.auditar(repo, reglas)))

    assert ".claude/tmp/migrar.ps1" in datos["rutas"]
    assert datos["conteo"][ss.MATERIAL_DE_CLIENTE] >= 3
    assert all("remedio" in h for h in datos["hallazgos"])


def test_binario_grande_no_tumba_la_auditoria(tmp_path, reglas):
    """El historial se recorre en CI: un blob binario no puede romper el gate."""
    repo = repo_limpio(tmp_path)
    (repo / "logo.bin").write_bytes(b"\x00\x01\x02" * 5000)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "binario")

    assert not ha.auditar(repo, reglas).hallazgos


def test_cli_sale_con_1_si_hay_bloqueantes(tmp_path, reglas, capsys):
    repo = repo_limpio(tmp_path)
    ensuciar(repo)

    assert ha.main(["--repo", str(repo)]) == 1
    assert ha.main(["--repo", str(repo_limpio(tmp_path, "otro"))]) == 0


def test_cli_falla_con_2_si_las_reglas_no_existen(tmp_path, capsys):
    repo = repo_limpio(tmp_path)
    assert ha.main(["--repo", str(repo), "--reglas", str(tmp_path / "nada.json")]) == 2
    assert "error:" in capsys.readouterr().err
