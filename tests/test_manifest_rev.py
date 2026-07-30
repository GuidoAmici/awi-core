"""Tests del pin de una dependencia — el `rev` del ADR 0012.

Estaba decidido y sin implementar, diferido por asumir que dependía del sustrato.
No depende: `agency-agents` es un repo de terceros en cualquier escenario, y el
riesgo que el `rev` cierra —un rename upstream que rompe una skill en silencio— es
de hoy, no de un destino hipotético. Ver PRD 5 (issue #84), subissue #106.

El que importa es `test_un_repo_pinneado_en_otro_commit_reporta_drift_y_no_se_corrige`:
corregirlo en silencio sería mover al operador de donde está, que es exactamente lo
que la materialización no puede hacer.
"""

import subprocess
from pathlib import Path

import pytest

from manifest import Repo, materialise_target


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    assert r.returncode == 0, f"git {' '.join(args)} falló: {r.stderr}"
    return r


@pytest.fixture
def upstream(tmp_path):
    """Un repo de terceros con dos commits y un tag: v1 y la punta."""
    r = tmp_path / "upstream"
    r.mkdir()
    git(r, "init", "-q", "-b", "main")
    git(r, "config", "user.email", "u@t")
    git(r, "config", "user.name", "u")
    (r / "rol.md").write_text("versión estable\n")
    git(r, "add", "-A")
    git(r, "commit", "-qm", "v1")
    git(r, "tag", "v1")
    primero = git(r, "rev-parse", "HEAD").stdout.strip()

    # Lo que un tercero puede hacer sin aviso: renombrar el archivo de un rol.
    git(r, "mv", "rol.md", "rol-renombrado.md")
    (r / "rol-renombrado.md").write_text("cambió sin aviso\n")
    git(r, "commit", "-qam", "rename upstream")
    return r, primero


# ── Pinear ────────────────────────────────────────────────────────────────────

def test_sin_rev_materializa_la_punta(upstream, tmp_path):
    r, _ = upstream
    destino = tmp_path / "flotante"

    estado, err = materialise_target(destino, str(r), "main")

    assert estado == "cloned", err
    assert (destino / "rol-renombrado.md").exists()


def test_con_rev_materializa_ese_commit(upstream, tmp_path):
    """El caso que el ADR 0012 motiva: el rename upstream no llega."""
    r, primero = upstream
    destino = tmp_path / "pinneado"

    estado, err = materialise_target(destino, str(r), "main", rev=primero)

    assert estado == "cloned", err
    assert (destino / "rol.md").read_text() == "versión estable\n"
    assert not (destino / "rol-renombrado.md").exists()


def test_un_tag_sirve_como_rev(upstream, tmp_path):
    r, _ = upstream
    destino = tmp_path / "por-tag"

    estado, err = materialise_target(destino, str(r), "main", rev="v1")

    assert estado == "cloned", err
    assert (destino / "rol.md").exists()


def test_un_rev_inexistente_falla_ruidosamente(upstream, tmp_path):
    r, _ = upstream

    estado, err = materialise_target(tmp_path / "roto", str(r), "main", rev="no-existe")

    assert estado == "failed"
    assert "no-existe" in err


# ── Drift ─────────────────────────────────────────────────────────────────────

def test_un_repo_pinneado_en_su_commit_esta_presente(upstream, tmp_path):
    r, primero = upstream
    destino = tmp_path / "ok"
    materialise_target(destino, str(r), "main", rev=primero)

    estado, err = materialise_target(destino, str(r), "main", rev=primero)

    assert estado == "present", err


def test_un_repo_pinneado_en_otro_commit_reporta_drift_y_no_se_corrige(upstream, tmp_path):
    """Corregirlo en silencio sería mover al operador de donde está."""
    r, primero = upstream
    destino = tmp_path / "movido"
    materialise_target(destino, str(r), "main")  # queda en la punta
    antes = git(destino, "rev-parse", "HEAD").stdout.strip()

    estado, err = materialise_target(destino, str(r), "main", rev=primero)

    assert estado == "drifted"
    assert primero[:7] in err or primero in err
    assert "deliberadamente" in err or "deliberately" in err
    assert git(destino, "rev-parse", "HEAD").stdout.strip() == antes, "movió el checkout"


def test_un_tag_y_su_commit_son_el_mismo_pin(upstream, tmp_path):
    """Reportar drift porque uno se escribe como tag sería ruido."""
    r, primero = upstream
    destino = tmp_path / "tag-vs-sha"
    materialise_target(destino, str(r), "main", rev="v1")

    estado, _ = materialise_target(destino, str(r), "main", rev=primero)

    assert estado == "present"


def test_sin_rev_un_repo_existente_nunca_es_drift(upstream, tmp_path):
    """Un contexto compartido flota: no hay nada de qué desviarse."""
    r, _ = upstream
    destino = tmp_path / "flota"
    materialise_target(destino, str(r), "main")
    git(destino, "checkout", "-q", "-b", "mi-rama")

    estado, err = materialise_target(destino, str(r), "main")

    assert estado == "present", err


# ── La política por categoría ─────────────────────────────────────────────────

def test_solo_una_dependencia_se_pinea():
    """Un org workspace es contexto compartido: pinearlo congelaría lo que su
    valor exige que esté al día. La distinción es la del ADR 0012."""
    dependencia = Repo(
        name="agency-agents", url="u", branch="main", path=Path("/x"),
        parent="AWI", upstream=True, rev="abc1234",
    )
    contexto = Repo(name="newhaze", url="u", branch="main", path=Path("/y"), parent="AWI")

    assert dependencia.is_pinned
    assert not contexto.is_pinned


def test_plan_ignora_el_rev_de_un_org_workspace(tmp_path):
    """Incluso si alguien lo escribe en el manifiesto: la política gana."""
    import json

    import manifest

    raiz = tmp_path / "awi"
    (raiz / "_data/users/1").mkdir(parents=True)
    (raiz / "_data/users/current-user.json").write_text(
        json.dumps({"github-id": "1", "login": "t"})
    )
    (raiz / "_data/users/1/user-submodules.json").write_text(json.dumps({
        "newhaze": {
            "url": "u", "path": "_data/organizations/newhaze", "branch": "main",
            "type": "org-workspace", "active": True, "rev": "abc1234",
        },
        "agency-agents": {
            "url": "u", "path": "_system/agency-agents", "branch": "main",
            "type": "system-repo", "active": True, "upstream": True, "rev": "abc1234",
        },
    }))

    repos, _ = manifest.plan(raiz)
    por_nombre = {r.name: r for r in repos}

    assert por_nombre["agency-agents"].rev == "abc1234"
    assert por_nombre["newhaze"].rev is None, "un contexto compartido no se pinea"
