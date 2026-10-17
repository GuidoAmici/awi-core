"""Barrido de worktrees: borra sólo lo que no puede perder nada."""
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import worktree as wt


def run(cwd: Path, *args: str) -> str:
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    principal = tmp_path / "repo"
    principal.mkdir()
    run(principal, "git", "init", "-q", "-b", "stg")
    run(principal, "git", "config", "user.email", "t@t")
    run(principal, "git", "config", "user.name", "t")
    (principal / "README.md").write_text("hola\n")
    run(principal, "git", "add", ".")
    run(principal, "git", "commit", "-qm", "inicial")
    return principal


def add_worktree(principal: Path, rama: str) -> dict:
    ruta = principal / wt.WORKTREES_SUBDIR / rama
    run(principal, "git", "worktree", "add", "-q", "-b", rama, str(ruta))
    (ruta / "cambio.txt").write_text("x\n")
    run(ruta, "git", "add", ".")
    run(ruta, "git", "commit", "-qm", "cambio")
    (encontrado,) = [w for w in wt.secondary_worktrees(principal) if w["path"] == ruta]
    return encontrado


def pr_cerrado(head: str, horas: float = 3, state: str = "MERGED") -> dict:
    cerrado = datetime.now(timezone.utc) - timedelta(hours=horas)
    return {"number": 7, "state": state, "headRefOid": head, "closedAt": cerrado.isoformat()}


def test_pr_mergeado_y_limpio_se_borra(repo):
    w = add_worktree(repo, "feat-a")
    assert wt.sweep_verdict(w, pr_cerrado(w["head"])) is None


def test_pr_abierto_o_recien_cerrado_se_conserva(repo):
    w = add_worktree(repo, "feat-a")
    assert wt.sweep_verdict(w, {**pr_cerrado(w["head"]), "state": "OPEN"}) == "con PR abierto"
    assert "menos de" in wt.sweep_verdict(w, pr_cerrado(w["head"], horas=0.5))


def test_sin_pr_se_conserva(repo):
    w = add_worktree(repo, "feat-a")
    assert wt.sweep_verdict(w, None) == "sin PR"


def test_cambios_sin_commitear_se_conservan(repo):
    w = add_worktree(repo, "feat-a")
    (w["path"] / "nuevo.txt").write_text("sin guardar\n")
    assert wt.sweep_verdict(w, pr_cerrado(w["head"])) == "con cambios sin commitear"


def test_commit_que_no_entro_al_pr_se_conserva(repo):
    w = add_worktree(repo, "feat-a")
    head_del_pr = w["head"]
    (w["path"] / "despues.txt").write_text("y\n")
    run(w["path"], "git", "add", ".")
    run(w["path"], "git", "commit", "-qm", "después del merge")
    w = wt.secondary_worktrees(repo)[0]
    assert wt.sweep_verdict(w, pr_cerrado(head_del_pr)) == "con commits que no están en el remoto"


def test_archivo_de_provision_no_cuenta_como_cambio_y_se_borra(repo):
    w = add_worktree(repo, "feat-a")
    (w["path"] / wt.PORT_FILE).write_text("3001\n")
    pr = pr_cerrado(w["head"])
    assert wt.sweep_verdict(w, pr) is None
    assert wt.remove_worktree(repo, w, pr) is None
    assert not w["path"].exists()
    assert run(repo, "git", "branch", "--list", "feat-a") == ""


def test_puerto_versionado_no_se_toca(repo):
    """2026-10-17: ramas viejas commitearon `.worktree-port` y el barrido lo borraba."""
    w = add_worktree(repo, "feat-a")
    (w["path"] / wt.PORT_FILE).write_text("3001\n")
    run(w["path"], "git", "add", wt.PORT_FILE)
    run(w["path"], "git", "commit", "-qm", "puerto versionado")
    w = wt.secondary_worktrees(repo)[0]
    pr = pr_cerrado(w["head"])
    assert wt.remove_worktree(repo, w, pr) is None
    assert not w["path"].exists()


def test_pr_cerrado_sin_merge_conserva_la_rama(repo):
    w = add_worktree(repo, "feat-a")
    pr = pr_cerrado(w["head"], state="CLOSED")
    assert wt.remove_worktree(repo, w, pr) is None
    assert run(repo, "git", "branch", "--list", "feat-a").strip("* ") == "feat-a"
