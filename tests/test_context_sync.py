"""Tests del ciclo de contexto compartido.

El que importa es `test_conflicto_no_deja_el_repo_a_medias`: es la regresión del
bug que hizo que el operador dejara de usar `/awi-sync`. Ante un rebase fallido,
aquel marcaba `failed`, retornaba y seguía con el próximo repo sin abortar,
dejando el repo a mitad de una operación que hay que sacar con comandos de git —
a personas que por diseño no usan git.
"""

import subprocess
from pathlib import Path

import pytest

import context_sync as cs
from manifest import Repo


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    assert r.returncode == 0, f"git {' '.join(args)} falló: {r.stderr}"
    return r


def make_repo(tmp_path: Path, name: str) -> tuple[Repo, Path, Path]:
    """Un remoto y dos clones: el operador local y un compañero."""
    remote = tmp_path / f"{name}.git"
    git(tmp_path, "init", "--bare", "-q", "-b", "only", str(remote))

    seed = tmp_path / f"{name}-seed"
    git(tmp_path, "clone", "-q", str(remote), str(seed))
    git(seed, "config", "user.email", "seed@t"); git(seed, "config", "user.name", "Seed")
    (seed / "nota.md").write_text("línea original\n")
    git(seed, "add", "-A"); git(seed, "commit", "-qm", "inicial")
    git(seed, "push", "-q", "origin", "only")

    local = tmp_path / f"{name}-local"
    other = tmp_path / f"{name}-other"
    for p, who in ((local, "local"), (other, "compa")):
        git(tmp_path, "clone", "-q", "--branch", "only", str(remote), str(p))
        git(p, "config", "user.email", f"{who}@t"); git(p, "config", "user.name", who)

    repo = Repo(name=name, url=str(remote), branch="only", path=local, parent="AWI")
    return repo, local, other


def test_pull_trae_los_cambios_del_otro(tmp_path):
    repo, local, other = make_repo(tmp_path, "org")
    (other / "nota.md").write_text("línea original\nagregado por el compañero\n")
    git(other, "commit", "-qam", "aporte del compañero")
    git(other, "push", "-q", "origin", "only")

    res = cs.pull_one(repo)

    assert res.state == "pulled"
    assert "compañero" in (local / "nota.md").read_text()


def test_pull_sin_novedades_reporta_al_dia(tmp_path):
    repo, _, _ = make_repo(tmp_path, "org")
    assert cs.pull_one(repo).state == "al-día"


def test_pull_con_arbol_sucio_no_pierde_los_cambios(tmp_path):
    """El árbol sucio es el estado normal al abrir sesión: --autostash lo permite."""
    repo, local, other = make_repo(tmp_path, "org")
    (other / "otro.md").write_text("del compañero\n")
    git(other, "add", "-A"); git(other, "commit", "-qm", "archivo nuevo")
    git(other, "push", "-q", "origin", "only")
    (local / "borrador.md").write_text("mi trabajo sin commitear\n")

    res = cs.pull_one(repo)

    assert res.state == "pulled"
    assert (local / "otro.md").exists(), "no trajo lo del compañero"
    assert (local / "borrador.md").read_text() == "mi trabajo sin commitear\n", "perdió mi borrador"


def test_conflicto_no_deja_el_repo_a_medias(tmp_path):
    """La regresión. Dos operadores editan la misma línea."""
    repo, local, other = make_repo(tmp_path, "org")

    (other / "nota.md").write_text("versión del compañero\n")
    git(other, "commit", "-qam", "cambio del compañero")
    git(other, "push", "-q", "origin", "only")

    (local / "nota.md").write_text("mi versión\n")
    git(local, "commit", "-qam", "mi cambio")

    res = cs.pull_one(repo)

    assert res.state == "conflicto"
    # Lo que rompía antes: el repo quedaba a mitad del rebase.
    assert not (local / ".git" / "rebase-merge").exists(), "quedó a mitad de un rebase"
    assert not (local / ".git" / "rebase-apply").exists(), "quedó a mitad de un rebase"
    # Y mi commit sigue estando.
    assert git(local, "log", "-1", "--format=%s").stdout.strip() == "mi cambio"
    assert (local / "nota.md").read_text() == "mi versión\n"


def test_conflicto_deja_el_repo_operable(tmp_path):
    """Después de un conflicto se puede seguir trabajando sin saber git."""
    repo, local, other = make_repo(tmp_path, "org")
    (other / "nota.md").write_text("del compañero\n")
    git(other, "commit", "-qam", "suyo"); git(other, "push", "-q", "origin", "only")
    (local / "nota.md").write_text("mío\n")
    git(local, "commit", "-qam", "mío")

    cs.pull_one(repo)

    # Un commit nuevo tiene que poder hacerse: si el repo estuviera a medias, falla.
    (local / "otra.md").write_text("sigo trabajando\n")
    git(local, "add", "-A")
    git(local, "commit", "-qm", "trabajo posterior al conflicto")


def test_push_usa_el_mensaje_que_le_pasan(tmp_path):
    """El mensaje llega por parámetro: /awi-sync usaba una constante y el
    historial compartido quedó siendo una pared de líneas idénticas."""
    repo, local, _ = make_repo(tmp_path, "org")
    (local / "nuevo.md").write_text("contenido\n")

    res = cs.push_one(repo, "docs(nota): agregar el resumen de la reunión")

    assert res.state == "publicado"
    assert git(local, "log", "-1", "--format=%s").stdout.strip() == \
        "docs(nota): agregar el resumen de la reunión"


def test_push_sin_nada_no_inventa_un_commit(tmp_path):
    repo, _, _ = make_repo(tmp_path, "org")
    assert cs.push_one(repo, "no debería usarse").state == "al-día"


def test_push_rechaza_si_el_remoto_adelanto(tmp_path):
    repo, local, other = make_repo(tmp_path, "org")
    (other / "suyo.md").write_text("x\n")
    git(other, "add", "-A"); git(other, "commit", "-qm", "suyo"); git(other, "push", "-q", "origin", "only")
    (local / "mio.md").write_text("y\n")

    res = cs.push_one(repo, "feat: lo mío")

    assert res.state == "conflicto"
    assert "traé primero" in res.detail


def test_sin_clonar_se_reporta_y_no_explota(tmp_path):
    repo = Repo(name="fantasma", url="x", branch="only", path=tmp_path / "no-existe", parent="AWI")
    assert cs.pull_one(repo).state == "sin-clonar"
    assert cs.push_one(repo, "m").state == "sin-clonar"
