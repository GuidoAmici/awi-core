"""gh-auth-pre.py sólo pushea cuando hay commits locales sin subir."""

import importlib.util
import subprocess
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "gh-auth-pre.py"


def load_hook():
    spec = importlib.util.spec_from_file_location("gh_auth_pre", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sh(*args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


def clone_with_readonly_push(tmp_path: Path) -> Path:
    """Clon al día con su origin, cuyo push URL no existe: pushear falla."""
    origin = tmp_path / "origin.git"
    seed = tmp_path / "seed"
    sh("git", "init", "-q", "--bare", "-b", "main", str(origin), cwd=tmp_path)
    sh("git", "init", "-q", "-b", "main", str(seed), cwd=tmp_path)
    sh("git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
       "--allow-empty", "-m", "init", cwd=seed)
    sh("git", "push", "-q", str(origin), "main", cwd=seed)
    clone = tmp_path / "clone"
    sh("git", "clone", "-q", str(origin), str(clone), cwd=tmp_path)
    sh("git", "remote", "set-url", "--push", "origin", str(tmp_path / "no-existe.git"), cwd=clone)
    return clone


def test_repo_limpio_y_al_dia_no_pushea(tmp_path):
    clone = clone_with_readonly_push(tmp_path)
    assert load_hook().commit_and_push("upstream", clone) is None


def test_commit_sin_pushear_intenta_el_push_y_reporta_el_fallo(tmp_path):
    clone = clone_with_readonly_push(tmp_path)
    sh("git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
       "--allow-empty", "-m", "local", cwd=clone)
    err = load_hook().commit_and_push("upstream", clone)
    assert err is not None and err.startswith("upstream: push failed")
