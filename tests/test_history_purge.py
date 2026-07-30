"""Tests de la purga.

El que sostiene todo es `test_la_verificacion_falla_si_no_se_purgo`: sin él, un
test que asevera «después de purgar la auditoría vuelve vacía» pasaría también
contra un repo que nadie purgó, y no probaría nada.
"""

import json
import subprocess
from pathlib import Path

import pytest

import history_audit as ha
import history_purge as hp
import sensitive_scan as ss
from paths import AWI_ROOT

filter_repo = pytest.mark.skipif(
    not hp.filter_repo_disponible(), reason="git-filter-repo no está instalado"
)


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    assert r.returncode == 0, f"git {' '.join(args)} falló: {r.stderr}"
    return r


@pytest.fixture
def reglas():
    return ss.cargar_reglas(AWI_ROOT / ss.REGLAS_SENSIBLES)


@pytest.fixture
def sucio(tmp_path: Path) -> Path:
    """Un repo con el escenario real: material plantado y después desversionado."""
    repo = tmp_path / "sucio"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@t")
    git(repo, "config", "user.name", "T")
    (repo / "README.md").write_text("# proyecto\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "inicial")

    tmp = repo / ".claude/tmp/delegates/issue-9"
    tmp.mkdir(parents=True)
    (tmp / "output.log").write_text("auditoría del cliente\n3 critical, 7 high issues found\n")
    (tmp / "status.json").write_text(json.dumps({"estado": "done"}))
    (repo / ".claude/tmp/migrar.ps1").write_text('$key = "sbp_' + "a1b2c3d4" * 5 + '"\n')
    # Un archivo legítimo con una línea sensible: la clase que exige decisión.
    (repo / "agenda.md").write_text(
        "# Semana\n\n- revisión publicada: 3 critical, 7 high, 10 medium\n- resto normal\n"
    )
    git(repo, "add", "-Af")
    git(repo, "commit", "-qm", "scratch y agenda")

    git(repo, "rm", "-r", "-q", "--cached", ".claude/tmp")
    (repo / ".gitignore").write_text(".claude/tmp/\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "desversionar el scratch")
    return repo


# ── El plan distingue las dos clases de hallazgo ───────────────────────────────

def test_el_plan_separa_ruta_de_contenido(sucio, reglas):
    plan = hp.planificar(ha.auditar(sucio, reglas))

    assert ".claude/tmp/migrar.ps1" in plan.por_ruta
    assert ".claude/tmp/delegates/issue-9/output.log" in plan.por_ruta
    assert plan.por_contenido == ["agenda.md"], (
        "un archivo legítimo con una línea sensible no se purga entero sin decidirlo"
    )


def test_el_plan_ignora_el_ruido_operativo(tmp_path, reglas):
    """Un .bak no justifica reescribir el historial de un repo público."""
    repo = tmp_path / "ruidoso"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@t")
    git(repo, "config", "user.name", "T")
    (repo / "nota.md.bak").write_text("copia\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "respaldo")

    plan = hp.planificar(ha.auditar(repo, reglas))

    assert plan.rutas(incluir_contenido=True) == []


def test_una_ruta_con_las_dos_clases_se_purga_entera(sucio, reglas):
    """output.log dispara por ruta y por contenido: no puede quedar duplicada."""
    plan = hp.planificar(ha.auditar(sucio, reglas))
    ruta = ".claude/tmp/delegates/issue-9/output.log"
    assert ruta in plan.por_ruta
    assert ruta not in plan.por_contenido


# ── La purga y su verificación ────────────────────────────────────────────────

@filter_repo
def test_purgar_saca_el_material_del_historial(sucio, tmp_path, reglas):
    r = hp.purgar(sucio, tmp_path / "espejo.git", reglas)

    residual = ha.auditar(r.espejo, reglas).rutas()
    assert not [x for x in residual if x.startswith(".claude/tmp/")]
    assert r.residuo == []
    assert len(r.despues.hallazgos) < len(r.antes.hallazgos)


@filter_repo
def test_la_verificacion_falla_si_no_se_purgo(sucio, reglas):
    """El test que hace que los demás valgan algo.

    Si `verificar` diera limpio contra un repo intacto, «después de purgar está
    limpio» sería una afirmación vacía.
    """
    rutas = hp.planificar(ha.auditar(sucio, reglas)).rutas()

    residuo = hp.verificar(sucio, reglas, rutas)

    assert residuo, "verificar aprobó un repo que nadie purgó"


def test_la_verificacion_no_aprueba_una_ruta_que_nunca_estuvo_en_la_lista(sucio, reglas):
    """La segunda regresión de la primera purga real.

    Verificar sólo contra la lista de rutas purgadas es circular: una ruta que el
    inventario nunca vio queda aprobada por no estar en la lista. Replanificar
    sobre el resultado es lo que rompe la circularidad.
    """
    residuo = hp.verificar(sucio, reglas, purgadas=["una/ruta/que/no/existe"])

    assert residuo, "aprobó un repo lleno de material con una lista vacía de rutas"
    assert any(h.ruta.startswith(".claude/tmp/") for h in residuo)


@filter_repo
def test_lo_legitimo_sobrevive(sucio, tmp_path, reglas):
    r = hp.purgar(sucio, tmp_path / "espejo.git", reglas)

    archivos = subprocess.run(
        ["git", "-C", str(r.espejo), "ls-tree", "-r", "--name-only", "HEAD"],
        capture_output=True, text=True,
    ).stdout.split()
    assert "README.md" in archivos
    assert "agenda.md" in archivos, "sin --incluir-contenido, agenda.md se queda"


@filter_repo
def test_incluir_contenido_se_lleva_la_ruta_entera(sucio, tmp_path, reglas):
    """El precio de la opción, aseverado: no redacta la línea, borra el archivo."""
    r = hp.purgar(sucio, tmp_path / "espejo.git", reglas, incluir_contenido=True)

    archivos = subprocess.run(
        ["git", "-C", str(r.espejo), "ls-tree", "-r", "--name-only", "HEAD"],
        capture_output=True, text=True,
    ).stdout.split()
    assert "agenda.md" not in archivos
    assert "README.md" in archivos


@filter_repo
def test_el_repo_original_no_se_toca(sucio, tmp_path, reglas):
    antes = git(sucio, "rev-parse", "HEAD").stdout.strip()
    conteo_antes = len(ha.auditar(sucio, reglas).hallazgos)

    hp.purgar(sucio, tmp_path / "espejo.git", reglas)

    assert git(sucio, "rev-parse", "HEAD").stdout.strip() == antes
    assert len(ha.auditar(sucio, reglas).hallazgos) == conteo_antes


@filter_repo
def test_alcanza_una_rama_no_mergeada(sucio, tmp_path, reglas):
    """`--mirror`: una rama abandonada sigue publicando lo que tiene."""
    git(sucio, "checkout", "-q", "-b", "abandonada")
    (sucio / ".claude").mkdir(exist_ok=True)
    escondido = sucio / ".claude/tmp"
    escondido.mkdir(parents=True, exist_ok=True)
    (escondido / "olvidado.ps1").write_text('$k = "sbp_' + "f0f0f0f0" * 5 + '"\n')
    git(sucio, "add", "-Af")
    git(sucio, "commit", "-qm", "en una rama que nadie mergeó")
    git(sucio, "checkout", "-q", "main")

    r = hp.purgar(sucio, tmp_path / "espejo.git", reglas)

    assert ".claude/tmp/olvidado.ps1" in r.purgadas
    assert not [x for x in ha.auditar(r.espejo, reglas).rutas() if x.startswith(".claude/tmp/")]


@filter_repo
def test_el_destino_existente_no_se_sobreescribe(sucio, tmp_path, reglas):
    destino = tmp_path / "ocupado.git"
    destino.mkdir()

    with pytest.raises(hp.PurgaFallida, match="ya existe"):
        hp.purgar(sucio, destino, reglas)


def test_un_repo_limpio_no_tiene_nada_que_purgar(tmp_path, reglas):
    repo = tmp_path / "limpio"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@t")
    git(repo, "config", "user.name", "T")
    (repo / "README.md").write_text("# nada\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "inicial")

    with pytest.raises(hp.PurgaFallida, match="ninguna ruta"):
        hp.purgar(repo, tmp_path / "espejo.git", reglas)


# ── El límite se dice siempre ──────────────────────────────────────────────────

@filter_repo
def test_el_resultado_declara_lo_que_no_garantiza(sucio, tmp_path, reglas):
    texto = hp.describir_resultado(hp.purgar(sucio, tmp_path / "espejo.git", reglas))
    assert "NO garantiza borrado en GitHub" in texto
    assert "comprometida" in texto


# ── CLI ───────────────────────────────────────────────────────────────────────

def test_sin_ejecutar_no_crea_nada(sucio, tmp_path, capsys):
    destino = tmp_path / "espejo.git"

    assert hp.main(["--repo", str(sucio), "--destino", str(destino)]) == 0

    assert not destino.exists()
    salida = capsys.readouterr().out
    assert "no se creó ni se modificó nada" in salida
    assert "agenda.md" in salida, "el plan tiene que nombrar lo que deja afuera"
