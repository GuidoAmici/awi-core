"""Tests del hook de pre-commit.

Lo que verifican es comportamiento externo: dado un índice con material
plantado, el commit no entra; dado un índice limpio, sí. Nunca la forma interna
del mensaje.

El par de tests que sostiene el diseño es
`test_saltear_con_no_verify_queda_registrado` junto con
`test_un_commit_normal_no_registra_salteo`: sin el segundo, el primero pasaría
con un registro que anota todo y por lo tanto no dice nada.
"""

import subprocess
from pathlib import Path

import pytest

import sensitive_scan as ss
import staged_scan as st
from paths import AWI_ROOT

REGLAS = str(AWI_ROOT / ss.REGLAS_SENSIBLES)


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    assert r.returncode == 0, f"git {' '.join(args)} falló: {r.stderr}"
    return r


@pytest.fixture
def reglas():
    return ss.cargar_reglas(AWI_ROOT / ss.REGLAS_SENSIBLES)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Un repo con los hooks de AWI realmente instalados."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@t")
    git(repo, "config", "user.name", "T")
    (repo / "README.md").write_text("# proyecto\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "inicial")

    # Los hooks reales del repo, apuntados al escaneo con las reglas reales.
    hooks = repo / "hooks-awi"
    hooks.mkdir()
    scan = AWI_ROOT / ".claude/skills/shared/scripts/staged_scan.py"
    for nombre, modo in (("pre-commit", "--hook"), ("post-commit", "--registrar-salteo")):
        h = hooks / nombre
        h.write_text(
            "#!/usr/bin/env bash\n"
            f'exec python3 "{scan}" {modo} --repo "$(git rev-parse --show-toplevel)" '
            f'--reglas "{REGLAS}"\n'
        )
        h.chmod(0o755)
    git(repo, "config", "core.hooksPath", "hooks-awi")
    return repo


def commitear(repo: Path, *args: str) -> subprocess.CompletedProcess:
    """Sin assert: el punto de varios tests es que el commit falle."""
    return subprocess.run(
        ["git", "commit", "-m", "prueba", *args], cwd=repo, capture_output=True, text=True
    )


def commits(repo: Path) -> int:
    return int(git(repo, "rev-list", "--count", "HEAD").stdout.strip())


# ── El hook bloquea ──────────────────────────────────────────────────────────

def test_material_de_cliente_no_entra(repo):
    antes = commits(repo)
    tmp = repo / ".claude/tmp/delegates/issue-9"
    tmp.mkdir(parents=True)
    (tmp / "output.log").write_text("auditoría del cliente\n")
    git(repo, "add", "-Af")

    r = commitear(repo)

    assert r.returncode != 0
    assert commits(repo) == antes, "el commit entró igual"


def test_credencial_no_entra(repo):
    (repo / "config.yaml").write_text('db_password: "Tr0ub4dor3xyz"\n')
    git(repo, "add", "-A")

    assert commitear(repo).returncode != 0


def test_el_mensaje_dice_archivo_regla_y_remedio(repo):
    (repo / "config.yaml").write_text('db_password: "Tr0ub4dor3xyz"\n')
    git(repo, "add", "-A")

    salida = commitear(repo).stderr

    assert "config.yaml:1" in salida
    assert "asignacion-de-secreto" in salida
    assert "Doppler" in salida
    assert st.SALTEO in salida, "tiene que decir cómo saltearlo"


def test_el_mensaje_no_reproduce_la_credencial(repo):
    secreto = "Tr0ub4dor3xyz"
    (repo / "config.yaml").write_text(f"db_password: {secreto}\n")
    git(repo, "add", "-A")

    assert secreto not in commitear(repo).stderr


# ── El hook deja pasar lo que corresponde ─────────────────────────────────────

def test_un_commit_limpio_pasa(repo):
    antes = commits(repo)
    (repo / "nota.md").write_text("# nada sensible\n\nLa password no se pega acá.\n")
    git(repo, "add", "-A")

    r = commitear(repo)

    assert r.returncode == 0, r.stderr
    assert commits(repo) == antes + 1


def test_ruido_operativo_advierte_pero_pasa(repo):
    """La categoría gobierna la severidad, también en el hook."""
    antes = commits(repo)
    (repo / "viejo.md.bak").write_text("copia\n")
    git(repo, "add", "-A")

    r = commitear(repo)

    assert r.returncode == 0, r.stderr
    assert commits(repo) == antes + 1
    assert "artefacto-de-respaldo" in r.stderr, "tenía que advertir"


def test_borrar_material_sensible_no_se_bloquea(repo, reglas):
    """Bloquear el commit que saca el material sería exactamente al revés."""
    (repo / "basura.md.bak").write_text("x\n")
    git(repo, "add", "-A")
    commitear(repo, "--no-verify")

    git(repo, "rm", "-q", "basura.md.bak")

    assert not st.escanear_staging(repo, reglas).hallazgos


def test_escanea_el_indice_y_no_el_arbol_de_trabajo(repo, reglas):
    """`git add` y después editar: el hook mira lo que se va a commitear."""
    f = repo / "config.yaml"
    f.write_text('password: "Tr0ub4dor3xyz"\n')
    git(repo, "add", "-A")
    f.write_text("# limpio ahora, pero el índice tiene el secreto\n")

    assert st.escanear_staging(repo, reglas).bloqueantes


# ── Registro del salteo ──────────────────────────────────────────────────────

def test_saltear_con_no_verify_queda_registrado(repo):
    (repo / "config.yaml").write_text('db_password: "Tr0ub4dor3xyz"\n')
    git(repo, "add", "-A")
    assert commitear(repo).returncode != 0

    r = commitear(repo, "--no-verify")

    assert r.returncode == 0, "--no-verify es el mecanismo estándar: tiene que funcionar"
    registrados = st.salteos(repo)
    assert len(registrados) == 1
    assert git(repo, "rev-parse", "--short", "HEAD").stdout.strip() in registrados[0]


def test_un_commit_normal_no_registra_salteo(repo):
    """Sin esto, el registro anotaría todo y por lo tanto no diría nada."""
    (repo / "nota.md").write_text("limpio\n")
    git(repo, "add", "-A")
    assert commitear(repo).returncode == 0

    assert st.salteos(repo) == []


def test_el_hook_recuerda_los_salteos_previos(repo):
    (repo / "a.yaml").write_text('password: "Tr0ub4dor3xyz"\n')
    git(repo, "add", "-A")
    commitear(repo, "--no-verify")

    (repo / "b.yaml").write_text('password: "0tr0Secret0xyz"\n')
    git(repo, "add", "-A")
    salida = commitear(repo).stderr

    assert "salteo(s) registrado(s) antes" in salida


def test_el_registro_no_se_versiona(repo):
    """Un registro de salteos que se versiona es material nuevo en el árbol."""
    (repo / "a.yaml").write_text('password: "Tr0ub4dor3xyz"\n')
    git(repo, "add", "-A")
    commitear(repo, "--no-verify")

    assert st.salteos(repo)
    assert not git(repo, "status", "--porcelain").stdout.strip()


# ── Robustez: un hook roto no puede ser un tapón ──────────────────────────────

def test_reglas_ausentes_avisan_pero_no_traban_el_trabajo(repo, tmp_path):
    (repo / "nota.md").write_text("limpio\n")
    git(repo, "add", "-A")

    codigo = st.main(["--repo", str(repo), "--hook", "--reglas", str(tmp_path / "nada.json")])

    assert codigo == 0


def test_reglas_ausentes_dejan_el_commit_como_no_escaneado(repo, tmp_path):
    """La contracara del test anterior: dejar pasar no es aprobar."""
    (repo / "nota.md").write_text("limpio\n")
    git(repo, "add", "-A")
    st.main(["--repo", str(repo), "--hook", "--reglas", str(tmp_path / "nada.json")])

    commitear(repo, "--no-verify")

    assert st.salteos(repo), "un commit sin escanear tiene que quedar anotado"


# ── Instalación ──────────────────────────────────────────────────────────────

def test_instalar_apunta_hooks_path(tmp_path):
    repo = tmp_path / "nuevo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")

    st.instalar(repo)

    assert git(repo, "config", "--get", "core.hooksPath").stdout.strip() == st.HOOKS_RELDIR


def test_instalar_es_idempotente(tmp_path):
    repo = tmp_path / "nuevo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")

    st.instalar(repo)
    segunda = st.instalar(repo)

    assert "ya instalado" in segunda


def test_los_hooks_versionados_existen_y_son_ejecutables():
    for nombre in ("pre-commit", "post-commit"):
        h = AWI_ROOT / st.HOOKS_RELDIR / nombre
        assert h.is_file(), f"falta {h}"
        assert h.stat().st_mode & 0o111, f"{h} no es ejecutable"
