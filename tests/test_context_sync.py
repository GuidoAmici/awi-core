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


# ── Material sensible ────────────────────────────────────────────────────────
# Publicar dejó de pedir confirmación (ADR 0020), así que `git add -A` corre sin
# que nadie mire lo que barre. El hook de pre-commit no cubre estos repos:
# `core.hooksPath` apunta a un directorio del harness y ellos son repos aparte,
# en `_data/`. Sin estos tests, el ciclo publica credenciales en silencio.

def test_push_no_publica_una_credencial(tmp_path):
    repo, local, _ = make_repo(tmp_path, "org")
    (local / ".env").write_text("DATABASE_URL=postgres://admin:s3cr3t0@db.example.com/prod\n")

    res = cs.push_one(repo, "chore: no debería llegar al remoto")

    assert res.state == "sensible"
    assert any(".env" in h for h in res.hallazgos)
    assert git(local, "log", "-1", "--format=%s").stdout.strip() == "inicial", "commiteó igual"


def test_push_bloqueado_no_toca_el_indice(tmp_path):
    """Escanear antes del `add` y no después: revertir un staging que el operador
    quizás armó a mano es otra forma de dejar el repo en un estado del que hay que
    salir con comandos de git."""
    repo, local, _ = make_repo(tmp_path, "org")
    (local / "a-mano.md").write_text("esto lo estageé yo\n")
    git(local, "add", "a-mano.md")
    (local / ".env").write_text("API_KEY=x\n")

    assert cs.push_one(repo, "chore: bloqueado").state == "sensible"

    estagiado = git(local, "diff", "--cached", "--name-only").stdout.split()
    assert estagiado == ["a-mano.md"], f"el índice cambió: {estagiado}"


def test_push_detecta_un_token_dentro_de_un_archivo_comun(tmp_path):
    """No alcanza con mirar la ruta: el caso real es una credencial pegada en una
    nota de agenda, que es markdown como cualquier otro."""
    repo, local, _ = make_repo(tmp_path, "org")
    (local / "daily.md").write_text("# Hoy\n\nla key de prod es AKIAIOSFODNN7EXAMPLE\n")

    res = cs.push_one(repo, "docs: daily")

    assert res.state == "sensible"
    assert any("daily.md" in h for h in res.hallazgos)


def test_push_no_filtra_la_credencial_en_su_propio_reporte(tmp_path):
    repo, local, _ = make_repo(tmp_path, "org")
    (local / "daily.md").write_text("token: AKIAIOSFODNN7EXAMPLE\n")

    res = cs.push_one(repo, "docs: daily")

    assert not any("AKIAIOSFODNN7EXAMPLE" in h for h in res.hallazgos), "el reporte filtra el secreto"


def test_push_publica_lo_que_no_es_sensible(tmp_path):
    """El escaneo no puede volverse un freno para el trabajo normal."""
    repo, local, _ = make_repo(tmp_path, "org")
    (local / "agenda.md").write_text("# Reunión\n\nDecidimos migrar en agosto.\n")

    assert cs.push_one(repo, "docs(agenda): resumen de la reunión").state == "publicado"


def test_sensible_cuenta_como_atencion_humana(tmp_path):
    repo, local, _ = make_repo(tmp_path, "org")
    (local / ".env").write_text("API_KEY=x\n")

    assert cs.report([cs.push_one(repo, "m")], "Prueba:") == cs.NEEDS_ATTENTION


# ── Rama activa distinta de la del manifiesto ────────────────────────────────
# Un codebase con una rama de feature checkeada es lo normal. El commit va a la
# rama activa y el push publica la del manifiesto: si no son la misma, publicar
# «con éxito» deja el trabajo en local mientras sube otra cosa.

def test_push_no_publica_desde_otra_rama(tmp_path):
    repo, local, _ = make_repo(tmp_path, "org")
    git(local, "checkout", "-q", "-b", "feat/algo")
    (local / "trabajo.md").write_text("mi feature\n")

    res = cs.push_one(repo, "feat: algo")

    assert res.state == "otra-rama"
    assert "feat/algo" in res.detail and "only" in res.detail
    assert git(local, "log", "-1", "--format=%s").stdout.strip() == "inicial", "commiteó igual"


def test_otra_rama_no_commitea_ni_estagea(tmp_path):
    repo, local, _ = make_repo(tmp_path, "org")
    git(local, "checkout", "-q", "-b", "feat/algo")
    (local / "trabajo.md").write_text("mi feature\n")

    cs.push_one(repo, "feat: algo")

    assert git(local, "diff", "--cached", "--name-only").stdout.strip() == ""
    assert (local / "trabajo.md").read_text() == "mi feature\n", "perdió el trabajo"


def test_otra_rama_cuenta_como_atencion_humana(tmp_path):
    repo, local, _ = make_repo(tmp_path, "org")
    git(local, "checkout", "-q", "-b", "feat/algo")
    (local / "trabajo.md").write_text("x\n")

    assert cs.report([cs.push_one(repo, "m")], "Prueba:") == cs.NEEDS_ATTENTION
